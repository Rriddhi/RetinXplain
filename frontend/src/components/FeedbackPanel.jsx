import React, { useState } from 'react'
import axios from 'axios'

function FeedbackPanel({ result, onFeedbackSubmitted }) {
  const [doctorGrade, setDoctorGrade] = useState(result.dr_grade.toString())
  const [comment, setComment] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)

    const formData = new FormData()
    formData.append('image_id', result.image_id)
    formData.append('ai_grade', result.dr_grade)
    formData.append('doctor_grade', parseInt(doctorGrade))
    formData.append('doctor_comment', comment)
    formData.append('confidence', result.confidence)

    try {
      const response = await axios.post('/feedback', formData)
      setSubmitted(true)
      setTimeout(() => {
        onFeedbackSubmitted()
      }, 2000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit feedback')
      setIsSubmitting(false)
    }
  }

  if (submitted) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center py-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-clinical-800 mb-2">Feedback Submitted</h3>
          <p className="text-clinical-600">Thank you for helping improve the system!</p>
        </div>
      </div>
    )
  }

  const isCorrect = parseInt(doctorGrade) === result.dr_grade

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="bg-clinical-600 text-white px-6 py-4">
        <h2 className="text-lg font-semibold">Clinician Feedback</h2>
        <p className="text-sm text-clinical-200 mt-1">Help improve the AI by providing your assessment</p>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-4">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-semibold text-clinical-700 mb-2">
            Your DR Grade Assessment
          </label>
          <select
            value={doctorGrade}
            onChange={(e) => setDoctorGrade(e.target.value)}
            className="w-full px-3 py-2 border border-clinical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isSubmitting}
          >
            <option value="0">Grade 0 - No DR</option>
            <option value="1">Grade 1 - Mild NPDR</option>
            <option value="2">Grade 2 - Moderate NPDR</option>
            <option value="3">Grade 3 - Severe NPDR</option>
            <option value="4">Grade 4 - Proliferative DR</option>
          </select>
          
          {!isCorrect && (
            <div className="mt-2 flex items-start text-sm">
              <svg className="w-4 h-4 text-yellow-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span className="text-yellow-700">
                Your assessment differs from the AI prediction (Grade {result.dr_grade})
              </span>
            </div>
          )}
          {isCorrect && (
            <div className="mt-2 flex items-start text-sm">
              <svg className="w-4 h-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-green-700">
                Your assessment matches the AI prediction
              </span>
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-semibold text-clinical-700 mb-2">
            Comments (Optional)
          </label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Add any observations or notes about this case..."
            rows={3}
            className="w-full px-3 py-2 border border-clinical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            disabled={isSubmitting}
          />
        </div>

        <div className="flex items-center justify-between pt-2">
          <p className="text-xs text-clinical-500">
            Feedback ID: {result.image_id}
          </p>
          <button
            type="submit"
            disabled={isSubmitting}
            className={`px-6 py-2 rounded-md font-semibold text-white transition-colors
              ${isSubmitting
                ? 'bg-clinical-300 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
              }
            `}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
          </button>
        </div>

        <div className="bg-clinical-50 rounded-lg p-3 text-xs text-clinical-600">
          <strong>Note:</strong> Your feedback helps the system learn and improve. Disagreements trigger 
          confidence threshold adjustments for future predictions.
        </div>
      </form>
    </div>
  )
}

export default FeedbackPanel
