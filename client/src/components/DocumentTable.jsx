import React, { useState, useEffect } from 'react'
import { documentApi } from '../services/api'
import { 
  FileText, 
  Upload, 
  Trash2, 
  Edit3, 
  Loader2, 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  FileUp, 
  X,
  RefreshCw
} from 'lucide-react'

export default function DocumentTable() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState(null)
  
  // Upload form state
  const [file, setFile] = useState(null)
  const [title, setTitle] = useState('')

  // Edit / Replace modal state
  const [editingDoc, setEditingDoc] = useState(null)
  const [editTitle, setEditTitle] = useState('')
  const [replaceFile, setReplaceFile] = useState(null)
  const [isUpdating, setIsUpdating] = useState(false)

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      const res = await documentApi.list()
      setDocuments(res.data)
    } catch (err) {
      console.error('Error fetching documents:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  // Poll for documents still in 'processing' status
  useEffect(() => {
    const hasProcessing = documents.some((d) => d.status === 'processing')
    if (!hasProcessing) return

    const interval = setInterval(async () => {
      try {
        const res = await documentApi.list()
        setDocuments(res.data)
      } catch (err) {
        console.error('Polling error:', err)
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [documents])

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file) {
      setUploadError('Please select a PDF file to upload.')
      return
    }

    try {
      setUploading(true)
      setUploadError(null)
      const formData = new FormData()
      formData.append('file', file)
      if (title.trim()) {
        formData.append('title', title.trim())
      }

      await documentApi.upload(formData)
      setFile(null)
      setTitle('')
      await fetchDocuments()
    } catch (err) {
      console.error('Upload error:', err)
      setUploadError(err.response?.data?.detail || 'Failed to upload document.')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (doc) => {
    if (!window.confirm(`Are you sure you want to delete "${doc.title}" and all its indexed embeddings?`)) {
      return
    }

    try {
      await documentApi.delete(doc.id)
      setDocuments((prev) => prev.filter((d) => d.id !== doc.id))
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete document.')
    }
  }

  const openEditModal = (doc) => {
    setEditingDoc(doc)
    setEditTitle(doc.title)
    setReplaceFile(null)
  }

  const handleUpdate = async (e) => {
    e.preventDefault()
    if (!editingDoc) return

    try {
      setIsUpdating(true)
      const formData = new FormData()
      if (editTitle.trim()) {
        formData.append('title', editTitle.trim())
      }
      if (replaceFile) {
        formData.append('file', replaceFile)
      }

      await documentApi.update(editingDoc.id, formData)
      setEditingDoc(null)
      await fetchDocuments()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update document.')
    } finally {
      setIsUpdating(false)
    }
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'ready':
        return (
          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="h-3 w-3" />
            Ready
          </span>
        )
      case 'processing':
        return (
          <span className="inline-flex items-center gap-1 rounded-full bg-amber-500/10 px-2.5 py-1 text-xs font-semibold text-amber-400 border border-amber-500/20">
            <Loader2 className="h-3 w-3 animate-spin" />
            Indexing...
          </span>
        )
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1 rounded-full bg-rose-500/10 px-2.5 py-1 text-xs font-semibold text-rose-400 border border-rose-500/20">
            <AlertTriangle className="h-3 w-3" />
            Failed
          </span>
        )
      default:
        return null
    }
  }

  return (
    <div className="space-y-8">
      {/* Upload Box Card */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm shadow-xl">
        <div className="flex items-center gap-3 mb-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600/20 text-indigo-400">
            <FileUp className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">Upload Official College Document</h3>
            <p className="text-xs text-slate-400">PDF documents will be parsed, chunked, and embedded into the vector store.</p>
          </div>
        </div>

        <form onSubmit={handleUpload} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                Document Title
              </label>
              <input
                type="text"
                placeholder="e.g. Academic Calendar 2026-27 or Hostel Regulations"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                PDF File (.pdf only)
              </label>
              <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={(e) => setFile(e.target.files[0])}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-300 file:mr-3 file:rounded-lg file:border-0 file:bg-indigo-600 file:px-3 file:py-1 file:text-xs file:font-semibold file:text-white hover:file:bg-indigo-500 cursor-pointer"
              />
            </div>
          </div>

          {uploadError && (
            <p className="text-xs text-rose-400 flex items-center gap-1.5">
              <AlertTriangle className="h-3.5 w-3.5" />
              {uploadError}
            </p>
          )}

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={uploading || !file}
              className="flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-md shadow-indigo-600/20 hover:bg-indigo-500 disabled:opacity-40 transition-all"
            >
              {uploading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Uploading & Chunking...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  Upload & Index
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Document Table Section */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-indigo-400" />
            <h3 className="font-semibold text-slate-100">Indexed Knowledge Documents</h3>
            <span className="rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-300">
              {documents.length}
            </span>
          </div>
          <button
            onClick={fetchDocuments}
            title="Refresh list"
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </button>
        </div>

        <div className="overflow-x-auto">
          {loading ? (
            <div className="flex items-center justify-center p-12 text-slate-400">
              <Loader2 className="h-6 w-6 animate-spin text-indigo-500" />
            </div>
          ) : documents.length === 0 ? (
            <div className="p-12 text-center text-slate-400">
              <FileText className="mx-auto h-10 w-10 text-slate-600 mb-3" />
              <p className="text-sm font-medium">No documents uploaded yet.</p>
              <p className="text-xs text-slate-500 mt-1">Upload PDF brochures, circulars, or schedules above.</p>
            </div>
          ) : (
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-800 bg-slate-950/60 text-xs uppercase text-slate-400">
                <tr>
                  <th className="px-6 py-3.5 font-semibold">Document Title</th>
                  <th className="px-6 py-3.5 font-semibold">Status</th>
                  <th className="px-6 py-3.5 font-semibold">Pages</th>
                  <th className="px-6 py-3.5 font-semibold">Uploaded</th>
                  <th className="px-6 py-3.5 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400">
                          <FileText className="h-4 w-4" />
                        </div>
                        <div>
                          <p className="font-semibold text-slate-100">{doc.title}</p>
                          <p className="text-xs text-slate-500">{doc.filename}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">{getStatusBadge(doc.status)}</td>
                    <td className="px-6 py-4 font-medium text-slate-300">
                      {doc.page_count > 0 ? `${doc.page_count} pages` : '—'}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {new Date(doc.uploaded_at).toLocaleDateString(undefined, {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => openEditModal(doc)}
                          title="Edit Document / Replace File"
                          className="rounded-lg p-1.5 text-slate-400 hover:bg-indigo-600/10 hover:text-indigo-400 transition-colors"
                        >
                          <Edit3 className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(doc)}
                          title="Delete Document"
                          className="rounded-lg p-1.5 text-slate-400 hover:bg-rose-500/10 hover:text-rose-400 transition-colors"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Edit / Replace Document Modal */}
      {editingDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="glass-panel w-full max-w-md rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h4 className="font-semibold text-slate-100">Edit / Replace Document</h4>
              <button
                onClick={() => setEditingDoc(null)}
                className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleUpdate} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
                  Replace PDF File (Optional)
                </label>
                <input
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={(e) => setReplaceFile(e.target.files[0])}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-300 file:mr-3 file:rounded-lg file:border-0 file:bg-indigo-600 file:px-2 file:py-1 file:text-xs file:text-white hover:file:bg-indigo-500"
                />
                <p className="mt-1 text-[11px] text-slate-500">
                  Uploading a new file will re-extract text, clear old chunks, and generate fresh embeddings.
                </p>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setEditingDoc(null)}
                  className="rounded-xl border border-slate-700 px-4 py-2 text-xs font-semibold text-slate-300 hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isUpdating}
                  className="flex items-center gap-1.5 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
                >
                  {isUpdating && <Loader2 className="h-3 w-3 animate-spin" />}
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
