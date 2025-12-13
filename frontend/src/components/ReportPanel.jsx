import React from 'react'

function ReportPanel({ result }) {
  const getGradeColor = (grade) => {
    const colors = {
      0: 'text-green-700 bg-green-50 border-green-200',
      1: 'text-blue-700 bg-blue-50 border-blue-200',
      2: 'text-yellow-700 bg-yellow-50 border-yellow-200',
      3: 'text-orange-700 bg-orange-50 border-orange-200',
      4: 'text-red-700 bg-red-50 border-red-200'
    }
    return colors[grade] || colors[0]
  }

  const getActionBadge = (action) => {
    const badges = {
      'urgent_referral': { text: 'Urgent Referral', color: 'bg-red-100 text-red-800' },
      'monitor_3_months': { text: 'Monitor 3 Months', color: 'bg-orange-100 text-orange-800' },
      'monitor_6_months': { text: 'Monitor 6 Months', color: 'bg-yellow-100 text-yellow-800' },
      'monitor_12_months': { text: 'Monitor 12 Months', color: 'bg-blue-100 text-blue-800' },
      'annual_screening': { text: 'Annual Screening', color: 'bg-green-100 text-green-800' },
      'needs_review': { text: 'Needs Review', color: 'bg-purple-100 text-purple-800' },
      'retake_image': { text: 'Retake Image', color: 'bg-gray-100 text-gray-800' }
    }
    return badges[action] || badges['annual_screening']
  }

  const actionBadge = getActionBadge(result.action)

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="bg-clinical-700 text-white px-6 py-4">
        <h2 className="text-xl font-semibold">Screening Results</h2>
      </div>

      <div className="p-6 space-y-6">
        <div className={`border-2 rounded-lg p-4 ${getGradeColor(result.dr_grade)}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium opacity-75">DR Grade</p>
              <p className="text-2xl font-bold">{result.grade_name}</p>
              <p className="text-sm mt-1">Grade {result.dr_grade} / 4</p>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium opacity-75">Confidence</p>
              <p className="text-2xl font-bold">{(result.confidence * 100).toFixed(1)}%</p>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-clinical-700 mb-2">Recommended Action</h3>
          <span className={`inline-block px-4 py-2 rounded-full text-sm font-semibold ${actionBadge.color}`}>
            {actionBadge.text}
          </span>
          {result.needs_review && (
            <span className="ml-2 inline-block px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-semibold">
              Flagged for Manual Review
            </span>
          )}
        </div>

        <div className="border-t pt-4">
          <h3 className="text-sm font-semibold text-clinical-700 mb-2">Clinician Summary</h3>
          <p className="text-clinical-600 text-sm leading-relaxed">
            {result.clinician_summary}
          </p>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-blue-900 mb-2 flex items-center">
            <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            Patient-Friendly Explanation
          </h3>
          <p className="text-clinical-700 text-sm leading-relaxed">
            {result.patient_summary}
          </p>
        </div>

        {result.gradcam_url && (
          <div>
            <h3 className="text-sm font-semibold text-clinical-700 mb-2">Explainability Visualization</h3>
            <p className="text-xs text-clinical-500 mb-3">
              Grad-CAM++ shows which regions influenced the AI's decision
            </p>
            <div className="border-2 border-clinical-200 rounded-lg overflow-hidden">
              <div className="bg-gradient-to-r from-red-500 to-yellow-500 text-white px-3 py-2 text-sm font-semibold">
                Grad-CAM++
              </div>
              <img 
                src={result.gradcam_url} 
                alt="Grad-CAM++ Heatmap" 
                className="max-w-full h-auto mx-auto"
              />
              <p className="text-xs text-clinical-500 p-2 bg-clinical-50">
                Heat colors show high-attention regions
              </p>
            </div>
          </div>
        )}

        <div className="bg-clinical-50 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-clinical-700 mb-2">Grade Probabilities</h3>
          <div className="space-y-2">
            {Object.entries(result.probabilities).map(([grade, prob]) => {
              const gradeNum = parseInt(grade.split('_')[1])
              const gradeName = ["No DR", "Mild", "Moderate", "Severe", "Proliferative"][gradeNum]
              return (
                <div key={grade} className="flex items-center">
                  <span className="text-xs font-medium text-clinical-600 w-24">{gradeName}</span>
                  <div className="flex-1 bg-clinical-200 rounded-full h-2 ml-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all"
                      style={{ width: `${prob * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-clinical-600 ml-2 w-12 text-right">
                    {(prob * 100).toFixed(1)}%
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ReportPanel
