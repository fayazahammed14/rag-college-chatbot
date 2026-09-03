-- ==============================================================================
-- CampusMind AI - Database Schema & Supabase Configuration
-- Run this in your Supabase SQL Editor to set up all tables, extensions, RLS policies,
-- and the pgvector similarity matching function.
-- ==============================================================================

-- 1. Enable the pgvector extension for AI embeddings
create extension if not exists vector;

-- 2. Drop existing objects if recreating (optional/safe order)
drop function if exists match_chunks(vector, float, int);
drop trigger if exists on_auth_user_created on auth.users;
drop function if exists public.handle_new_user();

-- 3. Profiles Table (Extends Supabase auth.users with role management)
create table if not exists public.profiles (
  id uuid references auth.users(id) on delete cascade primary key,
  name text,
  role text check (role in ('student', 'admin')) default 'student' not null,
  created_at timestamptz default now() not null
);

-- 4. Documents Table (Admin-uploaded college documents)
create table if not exists public.documents (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  filename text not null,
  uploaded_by uuid references auth.users(id) on delete set null,
  status text check (status in ('processing', 'ready', 'failed')) default 'processing' not null,
  page_count integer default 0 not null,
  uploaded_at timestamptz default now() not null,
  updated_at timestamptz default now() not null
);

-- 5. Document Chunks Table (Text segments with 768-dim embeddings from Gemini)
create table if not exists public.document_chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid references public.documents(id) on delete cascade not null,
  chunk_index integer not null,
  text text not null,
  embedding vector(768),
  page_number integer not null
);

-- Vector index for cosine similarity search
create index if not exists idx_document_chunks_embedding 
  on public.document_chunks 
  using hnsw (embedding vector_cosine_ops);

create index if not exists idx_document_chunks_document_id 
  on public.document_chunks (document_id);

-- 6. Conversations Table (Chat sessions)
create table if not exists public.conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  title text default 'New Conversation' not null,
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null
);

create index if not exists idx_conversations_user_id 
  on public.conversations (user_id);

-- 7. Messages Table (Chat history & sources)
create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid references public.conversations(id) on delete cascade not null,
  role text check (role in ('user', 'assistant')) not null,
  content text not null,
  sources jsonb default '[]'::jsonb not null,
  created_at timestamptz default now() not null
);

create index if not exists idx_messages_conversation_id 
  on public.messages (conversation_id);

-- ==============================================================================
-- 8. Helper Functions & Vector Search RPC
-- ==============================================================================

-- Helper to check if current user is an admin
create or replace function public.is_admin()
returns boolean as $$
begin
  return exists (
    select 1 from public.profiles
    where id = auth.uid() and role = 'admin'
  );
end;
$$ language plpgsql security definer;

-- Vector matching RPC function called by retrieval service
create or replace function match_chunks (
  query_embedding vector(768),
  match_threshold float default 0.4,
  match_count int default 5
)
returns table (
  id uuid,
  document_id uuid,
  chunk_index int,
  text text,
  page_number int,
  similarity float,
  document_title text
)
language sql stable
as $$
  select
    dc.id,
    dc.document_id,
    dc.chunk_index,
    dc.text,
    dc.page_number,
    1 - (dc.embedding <=> query_embedding) as similarity,
    d.title as document_title
  from public.document_chunks dc
  join public.documents d on d.id = dc.document_id
  where d.status = 'ready' 
    and dc.embedding is not null
    and (1 - (dc.embedding <=> query_embedding)) >= match_threshold
  order by similarity desc
  limit match_count;
$$;

-- Automatic user profile creation trigger
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, name, role, created_at)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'name', split_part(new.email, '@', 1)),
    coalesce(new.raw_user_meta_data->>'role', 'student'),
    now()
  )
  on conflict (id) do nothing;
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ==============================================================================
-- 9. Row Level Security (RLS) Policies
-- ==============================================================================

alter table public.profiles enable row level security;
alter table public.documents enable row level security;
alter table public.document_chunks enable row level security;
alter table public.conversations enable row level security;
alter table public.messages enable row level security;

-- PROFILES Policies
create policy "Authenticated users can view profiles"
  on public.profiles for select
  to authenticated
  using (true);

create policy "Users can update their own profile"
  on public.profiles for update
  to authenticated
  using (auth.uid() = id);

-- DOCUMENTS Policies
create policy "Authenticated users can view ready documents"
  on public.documents for select
  to authenticated
  using (status = 'ready' or public.is_admin());

create policy "Admins can insert documents"
  on public.documents for insert
  to authenticated
  with check (public.is_admin());

create policy "Admins can update documents"
  on public.documents for update
  to authenticated
  using (public.is_admin());

create policy "Admins can delete documents"
  on public.documents for delete
  to authenticated
  using (public.is_admin());

-- DOCUMENT CHUNKS Policies
create policy "Authenticated users can view document chunks"
  on public.document_chunks for select
  to authenticated
  using (true);

create policy "Admins can insert document chunks"
  on public.document_chunks for insert
  to authenticated
  with check (public.is_admin());

create policy "Admins can update document chunks"
  on public.document_chunks for update
  to authenticated
  using (public.is_admin());

create policy "Admins can delete document chunks"
  on public.document_chunks for delete
  to authenticated
  using (public.is_admin());

-- CONVERSATIONS Policies
create policy "Users can view their own conversations"
  on public.conversations for select
  to authenticated
  using (auth.uid() = user_id);

create policy "Users can create their own conversations"
  on public.conversations for insert
  to authenticated
  with check (auth.uid() = user_id);

create policy "Users can update their own conversations"
  on public.conversations for update
  to authenticated
  using (auth.uid() = user_id);

create policy "Users can delete their own conversations"
  on public.conversations for delete
  to authenticated
  using (auth.uid() = user_id);

-- MESSAGES Policies
create policy "Users can view messages in their conversations"
  on public.messages for select
  to authenticated
  using (
    exists (
      select 1 from public.conversations
      where conversations.id = messages.conversation_id
      and conversations.user_id = auth.uid()
    )
  );

create policy "Users can insert messages in their conversations"
  on public.messages for insert
  to authenticated
  with check (
    exists (
      select 1 from public.conversations
      where conversations.id = messages.conversation_id
      and conversations.user_id = auth.uid()
    )
  );
