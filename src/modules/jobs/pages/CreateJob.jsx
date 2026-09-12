import { useState } from 'react'
import { ArrowLeft, Check, Plus, Sparkles, Trash2, BriefcaseBusiness } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import ErrorBanner from '../../../core/components/ErrorBanner'
import { createJob } from '../../../core/api/api'

export default function CreateJob() {
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [department, setDepartment] = useState('')
  const [description, setDescription] = useState('')
  const [experienceMonths, setExperienceMonths] = useState(0)
  const [requirements, setRequirements] = useState([])
  const [newSkillInput, setNewSkillInput] = useState('')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [errorMsg, setErrorMsg] = useState(null)

  const handleAddRequirement = () => {
    if (!newSkillInput.trim()) return
    const skillName = newSkillInput.trim()
    if (requirements.some(r => r.skill.toLowerCase() === skillName.toLowerCase())) {
      setErrorMsg(`Skill '${skillName}' is already in the requirement list.`)
      return
    }
    setRequirements(old => [...old, { skill: skillName, type: 'Must Have', weight: 10 }])
    setNewSkillInput('')
    setErrorMsg(null)
  }

  const handleRemoveRequirement = (index) => {
    setRequirements(old => old.filter((_, i) => i !== index))
  }

  const handleSubmit = async (e) => {
    e?.preventDefault()
    setErrorMsg(null)

    if (!title.trim()) {
      setErrorMsg('Job title is required.')
      return
    }
    if (!description.trim()) {
      setErrorMsg('Job description is required.')
      return
    }

    if (requirements.some(r => r.weight === '' || !Number.isFinite(Number(r.weight)) || Number(r.weight) < 0)) {
      setErrorMsg('Requirement weights must be non-negative numbers.')
      return
    }
    const mustHaveSkills = requirements
      .filter(r => r.type === 'Must Have' || r.type === 'must_have')
      .map(r => r.skill)
    const preferredSkills = requirements
      .filter(r => r.type === 'Preferred' || r.type === 'preferred')
      .map(r => r.skill)

    const reqList = requirements.map((r, idx) => ({
      requirement_id: `REQ_${idx + 1}`,
      description: `Demonstrate proficiency in ${r.skill}`,
      skill: r.skill,
      category: 'competency',
      importance: r.type === 'Must Have' ? 'must_have' : 'preferred',
      mandatory: r.type === 'Must Have',
      weight: Number(r.weight) || 10
    }))

    const jobId = `JOB_${title.replace(/\s+/g, '_').toUpperCase()}_${Date.now().toString().slice(-4)}`

    const payload = {
      job_id: jobId,
      title: title.trim(),
      department: department.trim() || 'Engineering',
      status: 'Active',
      description: description.trim(),
      domain: ['Technology'],
      min_experience_months: Number(experienceMonths) || 0,
      must_have_skills: mustHaveSkills,
      preferred_skills: preferredSkills,
      requirements: reqList
    }

    setSaving(true)
    try {
      await createJob(payload)
      setSaved(true)
      setTimeout(() => {
        navigate('/jobs')
      }, 1000)
    } catch (err) {
      setErrorMsg(err.message || 'Failed to save job definition to database.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header Bar */}
      <div className="flex items-center justify-between">
        <Link
          to="/jobs"
          className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-bold text-slate-700 shadow-xs hover:bg-slate-50 transition"
        >
          <ArrowLeft size={14} /> Back to Jobs
        </Link>
      </div>

      {errorMsg && <ErrorBanner message={errorMsg} onClose={() => setErrorMsg(null)} />}

      {/* Main Form Panel */}
      <form onSubmit={handleSubmit} className="panel p-8 shadow-panel space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b border-slate-100">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-slate-900 to-apple-blue text-white shadow-md">
            <BriefcaseBusiness size={22} />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">Define Target Job Profile</h1>
            <p className="text-xs text-slate-500 font-medium">Specify mandatory requirements, minimum experience, and skill weights.</p>
          </div>
        </div>

        {/* Form Grid */}
        <div className="grid gap-6 sm:grid-cols-2">
          <div>
            <label className="eyebrow block mb-2 text-slate-700">Job Title *</label>
            <input
              type="text"
              required
              value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder="e.g. Senior Backend Engineer"
              className="w-full rounded-2xl border border-slate-200 bg-white p-3 text-xs font-semibold text-slate-900 outline-none focus:border-apple-blue focus:ring-2 focus:ring-apple-blue/20"
            />
          </div>

          <div>
            <label className="eyebrow block mb-2 text-slate-700">Department</label>
            <input
              type="text"
              value={department}
              onChange={e => setDepartment(e.target.value)}
              placeholder="e.g. Engineering / Product"
              className="w-full rounded-2xl border border-slate-200 bg-white p-3 text-xs font-semibold text-slate-900 outline-none focus:border-apple-blue focus:ring-2 focus:ring-apple-blue/20"
            />
          </div>
        </div>

        <div>
          <label className="eyebrow block mb-2 text-slate-700">Minimum Total Experience (Months)</label>
          <input
            type="number"
            min="0"
            value={experienceMonths}
            onChange={e => setExperienceMonths(Math.max(0, parseInt(e.target.value) || 0))}
            className="w-full rounded-2xl border border-slate-200 bg-white p-3 text-xs font-semibold text-slate-900 outline-none focus:border-apple-blue focus:ring-2 focus:ring-apple-blue/20"
          />
          <p className="mt-1 text-[11px] text-slate-400">Candidates below this threshold will trigger a mandatory rejection policy.</p>
        </div>

        <div>
          <label className="eyebrow block mb-2 text-slate-700">Job Description & Responsibilities *</label>
          <textarea
            rows={4}
            required
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="Describe role responsibilities, key project scope, and required candidate background..."
            className="w-full rounded-2xl border border-slate-200 bg-white p-3.5 text-xs font-medium text-slate-900 outline-none focus:border-apple-blue focus:ring-2 focus:ring-apple-blue/20"
          />
        </div>

        {/* Skill Requirement Tagger */}
        <div className="pt-4 border-t border-slate-100 space-y-4">
          <label className="eyebrow block text-slate-700">Add Skill Requirements</label>

          <div className="flex gap-2">
            <input
              type="text"
              value={newSkillInput}
              onChange={e => setNewSkillInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); handleAddRequirement() } }}
              placeholder="e.g. Python, FastAPI, PostgreSQL..."
              className="flex-1 rounded-2xl border border-slate-200 bg-white p-3 text-xs font-semibold text-slate-900 outline-none focus:border-apple-blue"
            />
            <button
              type="button"
              onClick={handleAddRequirement}
              className="btn-soft text-xs"
            >
              <Plus size={16} /> Add Skill
            </button>
          </div>

          {/* Added Skills List */}
          {requirements.length > 0 && (
            <div className="space-y-2.5">
              {requirements.map((req, idx) => (
                <div key={idx} className="flex items-center justify-between gap-3 rounded-2xl border border-slate-200/80 bg-slate-50 p-3 text-xs">
                  <span className="font-bold text-slate-900">{req.skill}</span>
                  <div className="flex items-center gap-3">
                    <select
                      value={req.type}
                      onChange={e => {
                        const val = e.target.value
                        setRequirements(old => old.map((r, i) => i === idx ? { ...r, type: val } : r))
                      }}
                      className="rounded-xl border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-slate-700"
                    >
                      <option value="Must Have">Must Have (Mandatory)</option>
                      <option value="Preferred">Preferred</option>
                    </select>

                    <button
                      type="button"
                      onClick={() => handleRemoveRequirement(idx)}
                      className="text-slate-400 hover:text-rose-600 transition"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Submit Actions */}
        <div className="pt-6 border-t border-slate-100 flex items-center justify-end gap-3">
          <Link to="/jobs" className="btn-soft text-xs">
            Cancel
          </Link>
          <button
            type="submit"
            disabled={saving || saved}
            className="btn-primary"
          >
            {saved ? (
              <>
                <Check size={16} /> Saved Successfully!
              </>
            ) : saving ? (
              <>Saving Job Profile...</>
            ) : (
              <>
                <Sparkles size={16} /> Save & Activate Job
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
