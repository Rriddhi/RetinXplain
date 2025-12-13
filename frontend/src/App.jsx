import React, { useState } from 'react'
import ImageUpload from './components/ImageUpload'
import ReportPanel from './components/ReportPanel'
import FeedbackPanel from './components/FeedbackPanel'

function App() {
  const [predictionResult, setPredictionResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handlePredictionComplete = (result) => {
    setPredictionResult(result)
    setIsLoading(false)
    setError(null)
  }

  const handlePredictionStart = () => {
    setIsLoading(true)
    setError(null)
    setPredictionResult(null)
  }

  const handleError = (errorMessage) => {
    setError(errorMessage)
    setIsLoading(false)
  }

  const handleFeedbackSubmitted = () => {
    setPredictionResult(null)
  }

  return (
    <div className="min-h-screen bg-clinical-50">
      <header className="bg-clinical-700 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold">RetinXplain+Agent</h1>
          <p className="text-clinical-200 mt-1">AI-Powered Diabetic Retinopathy Screening System</p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            <strong className="font-semibold">Error: </strong>
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-6">
            <ImageUpload
              onPredictionComplete={handlePredictionComplete}
              onPredictionStart={handlePredictionStart}
              onError={handleError}
              isLoading={isLoading}
            />
          </div>

          <div className="space-y-6">
            {predictionResult && (
              <>
                <ReportPanel result={predictionResult} />
                <FeedbackPanel
                  result={predictionResult}
                  onFeedbackSubmitted={handleFeedbackSubmitted}
                />
              </>
            )}
            
            {isLoading && (
              <div className="bg-white rounded-lg shadow-md p-8 text-center">
                <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-clinical-500 border-r-transparent"></div>
                <p className="mt-4 text-clinical-600">Analyzing retinal image...</p>
              </div>
            )}

            {!predictionResult && !isLoading && (
              <div className="bg-white rounded-lg shadow-md p-8 text-center text-clinical-400">
                <svg className="mx-auto h-16 w-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <p className="text-lg">Upload a fundus image to begin screening</p>
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="bg-clinical-700 text-clinical-300 mt-16">
        <div className="container mx-auto px-4 py-6 text-center text-sm">
          <p>RetinXplain+Agent v1.0 - For research and clinical decision support</p>
          <p className="mt-1">Always verify AI predictions with clinical judgment</p>
        </div>
      </footer>
    </div>
  )
}

export default App
