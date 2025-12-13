import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'

function ImageUpload({ onPredictionComplete, onPredictionStart, onError, isLoading }) {
  const [preview, setPreview] = useState(null)

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result)
      }
      reader.readAsDataURL(file)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    maxFiles: 1,
    disabled: isLoading
  })

  const handleSubmit = async () => {
    if (acceptedFiles.length === 0) {
      onError('Please select an image first')
      return
    }

    onPredictionStart()

    const formData = new FormData()
    formData.append('file', acceptedFiles[0])

    try {
      const response = await axios.post('/api/dr/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      onPredictionComplete(response.data)
    } catch (err) {
      onError(err.response?.data?.detail || 'Failed to process image. Please try again.')
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-clinical-800 mb-4">Upload Fundus Image</h2>
      
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-clinical-300 hover:border-clinical-400'}
          ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        {preview ? (
          <div>
            <img src={preview} alt="Preview" className="mx-auto max-h-64 rounded" />
            <p className="mt-2 text-sm text-clinical-600">
              {acceptedFiles[0]?.name}
            </p>
          </div>
        ) : (
          <div className="text-clinical-500">
            <svg className="mx-auto h-12 w-12 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            {isDragActive ? (
              <p>Drop the image here...</p>
            ) : (
              <p>Drag and drop a fundus image, or click to select</p>
            )}
            <p className="text-xs mt-2">Supports: JPG, PNG</p>
          </div>
        )}
      </div>

      <button
        onClick={handleSubmit}
        disabled={isLoading || acceptedFiles.length === 0}
        className={`mt-6 w-full py-3 px-4 rounded-md font-semibold text-white transition-colors
          ${isLoading || acceptedFiles.length === 0
            ? 'bg-clinical-300 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700'
          }
        `}
      >
        {isLoading ? 'Processing...' : 'Analyze Image'}
      </button>
    </div>
  )
}

export default ImageUpload
