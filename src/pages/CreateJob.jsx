import { useState } from 'react'
import { ArrowLeft, Check, Plus, Sparkles } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import ErrorBanner from '../components/ErrorBanner'
import { createJob } from '../services/api'

const initialRequirements = [
  { skill: 'Python', type: 'Must Have', weight: 10 },
  { skill: 'FastAPI', type: 'Preferred', weight: 8 },
  { skill: 'AWS', type: 'Preferred', weight: 6 }
]

export default function CreateJob() {
  const navigate = useNavigate()
  const [title, setTitle] = useState('Senior Backend Engineer')
  const [department, setDepartment] = useState('Engineering')
  const [description, setDescription] = useState('We are looking for a Senior Backend Engineer to design reliable APIs and services that power our next generation of products. You will own services from architecture through production and work closely with product and data teams.')
  const [requirements, setRequirements] = useState(initialRequirements)
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

    // User Error Validation
    if (!title.trim()) {
      setErrorMsg('Job title is required.')
      return
    }
    if (!description.trim()) {
      setErrorMsg('Job description is required.')
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
      description: `Proficiency in ${r.skill}`,
      skill: r.skill,
      importance: r.type === 'Must Have' ? 'must_have' : 'preferred',
      mandatory: r.type === 'Must Have',
      weight: Number(r.weight) || 10
    }))

    const jobId = `J_${Date.now().toString().slice(-6)}`
    const payload = {
      job_id: jobId,
      title: title.trim(),
      must_have_skills: mustHaveSkills,
      preferred_skills: preferredSkills,
      requirements: reqList,
      min_experience_months: 36,
      domain: [department]
    }

    setSaving(true)
    try {
      await createJob(payload)
      setSaved(true)
      setTimeout(() => {
        navigate('/jobs')
      }, 1000)
    } catch (err) {
      setErrorMsg(err.message || 'Failed to save job definition to backend. Please check backend connection.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl">
      <Link to="/jobs" className="mb-7 flex items-center gap-2 text-xs font-bold text-muted hover:text-ink">
        <ArrowLeft size={15} />Back to jobs
      </Link>

      <div className="mb-8">
        <p className="eyebrow mb-2">Job builder</p>
        <h1 className="text-3xl font-extrabold tracking-tight">Create a new job</h1>
        <p className="mt-2 text-sm text-muted">Describe the role and let HireLens extract what matters.</p>
      </div>

      {errorMsg && (
        <ErrorBanner message={errorMsg} onClose={() => setErrorMsg(null)} />
      )}

      <div className="grid gap-6 lg:grid-cols-[1fr_.8fr]">
        <section className="panel p-6">
          <form onSubmit={handleSubmit} className="space-y-5">
            <label className="block">
              <span className="mb-2 block text-xs font-bold">Job title *</span>
              <input
                value={title}
                onChange={e => setTitle(e.target.value)}
                className="w-full rounded-lg border bg-canvas px-3 py-3 text-sm outline-none focus:border-teal"
                placeholder="e.g. Senior Backend Engineer"
                required
              />
            </label>

            <label className="block">
              <span className="mb-2 block text-xs font-bold">Department</span>
              <select
                value={department}
                onChange={e => setDepartment(e.target.value)}
                className="w-full rounded-lg border bg-canvas px-3 py-3 text-sm outline-none focus:border-teal"
              >
                <option>Engineering</option>
                <option>Infrastructure</option>
                <option>Data & AI</option>
              </select>
            </label>

            <label className="block">
              <span className="mb-2 block text-xs font-bold">Job description *</span>
              <textarea
                value={description}
                onChange={e => setDescription(e.target.value)}
                className="min-h-48 w-full resize-y rounded-lg border bg-canvas px-3 py-3 text-sm leading-6 outline-none focus:border-teal"
                placeholder="Describe role responsibilities and requirements..."
                required
              />
            </label>

            <button
              type="submit"
              disabled={saving || saved}
              className="btn-primary w-full"
            >
              {saved ? (
                <><Check size={16} />Job saved! Redirecting...</>
              ) : saving ? (
                <>Saving to database...</>
              ) : (
                <><Sparkles size={16} />Save & Extract requirements</>
              )}
            </button>
          </form>
        </section>

        <section className="panel p-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <p className="eyebrow mb-2">AI extraction</p>
              <h2 className="text-xl font-extrabold">Requirements</h2>
            </div>
            <span className="rounded-full bg-mint px-2 py-1 text-[10px] font-bold text-teal">
              {requirements.length} found
            </span>
          </div>

          <div className="space-y-3">
            {requirements.map((req, index) => (
              <div key={`${req.skill}_${index}`} className="rounded-xl border bg-canvas p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold">{req.skill}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveRequirement(index)}
                    className="text-muted hover:text-coral"
                  >
                    ×
                  </button>
                </div>
                <div className="mt-3 flex items-center justify-between gap-2">
                  <select
                    value={req.type}
                    onChange={e => setRequirements(old => old.map((item, i) => i === index ? { ...item, type: e.target.value } : item))}
                    className="rounded-md border bg-white px-2 py-1.5 text-[11px] font-bold"
                  >
                    <option>Must Have</option>
                    <option>Preferred</option>
                  </select>

                  <label className="flex items-center gap-2 text-[11px] text-muted">
                    Weight
                    <input
                      type="number"
                      value={req.weight}
                      onChange={e => setRequirements(old => old.map((item, i) => i === index ? { ...item, weight: e.target.value } : item))}
                      className="w-12 rounded-md border bg-white px-2 py-1.5 text-center font-bold text-ink"
                    />
                  </label>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 flex gap-2">
            <input
              type="text"
              placeholder="New skill (e.g. Docker)"
              value={newSkillInput}
              onChange={e => setNewSkillInput(e.target.value)}
              className="flex-1 rounded-lg border bg-white px-3 py-2 text-xs outline-none focus:border-teal"
              onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); handleAddRequirement(); } }}
            />
            <button
              type="button"
              onClick={handleAddRequirement}
              className="btn-soft px-3"
            >
              <Plus size={15} />Add
            </button>
          </div>
        </section>
      </div>
    </div>
  )
}