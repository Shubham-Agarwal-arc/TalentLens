import React, { useState } from 'react';

const API_BASE = 'http://localhost:8000/api';

const SAMPLE_JD_TEXT = `Senior Full-Stack & Backend Software Engineer
We are seeking a Backend / Full-Stack Software Engineer with 4+ years of experience building scalable microservices and cloud-native web applications.

Key Requirements:
- 4+ years of hands-on software engineering experience in Python or Java.
- Strong proficiency in FastAPI, Spring Boot, REST APIs, and Microservices architecture.
- Experience with PostgreSQL, SQL, and Redis for high-throughput data storage.
- Frontend familiarity with React.js and TypeScript.
- Hands-on deployment experience using Docker, Kubernetes, AWS, and CI/CD pipelines.
- Bachelor's degree (B.Tech / B.E. / B.S.) in Computer Science or related field.`;

export default function App() {
  const [jdText, setJdText] = useState('');
  const [parsedJd, setParsedJd] = useState(null);
  const [resumeFiles, setResumeFiles] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [errors, setErrors] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [loading, setLoading] = useState(false);
  const [minScoreFilter, setMinScoreFilter] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [notice, setNotice] = useState('');

  // Module 1: Upload JD file and extract requirements immediately
  const handleJdFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('jd_file', file);

    try {
      const res = await fetch(`${API_BASE}/parse-jd`, { method: 'POST', body: formData });
      const data = await res.json();
      if (res.ok) {
        setJdText(data.jd_text);
        setParsedJd(data.parsed_jd);
        setNotice(`JD ready: ${data.parsed_jd.required_skills.length} skills detected`);
      } else {
        setNotice(data.detail || 'Failed to parse JD file');
      }
    } catch (err) {
      setNotice('Backend connection failed. Start the app with Start-AI-Resume-Matcher.bat.');
    }
  };

  // Module 2: Batch Resume Upload (PDF/DOCX)
  const handleResumeSelection = (e) => {
    const files = Array.from(e.target.files || []);
    setResumeFiles(files);
    setNotice(files.length ? `${files.length} resume${files.length === 1 ? '' : 's'} selected` : '');
  };

  // Module 3: Run AI Semantic Matching & Ranking
  const handleRunMatching = async () => {
    if (!jdText.trim()) {
      setNotice('Add a Job Description before running analysis.');
      return;
    }
    if (resumeFiles.length === 0) {
      setNotice('Select at least one PDF or DOCX resume before running analysis.');
      return;
    }

    setLoading(true);
    setErrors([]);
    try {
      const formData = new FormData();
      formData.append('jd_text', jdText);
      resumeFiles.forEach((file) => formData.append('resumes', file));

      const res = await fetch(`${API_BASE}/match`, { method: 'POST', body: formData });
      const data = await res.json();

      if (res.ok) {
        setParsedJd(data.parsed_jd);
        setCandidates(data.candidates);
        setErrors(data.errors || []);
        setNotice(`Analysis complete — ${data.candidates.length} candidates ranked`);
      } else {
        setNotice(data.detail || 'Error matching resumes');
      }
    } catch (err) {
      setNotice('Could not reach the backend. Start the app with Start-AI-Resume-Matcher.bat.');
    } finally {
      setLoading(false);
    }
  };

  const getScoreBadgeColor = (score) => {
    if (score >= 80) return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    if (score >= 60) return 'bg-amber-100 text-amber-800 border-amber-200';
    return 'bg-rose-100 text-rose-800 border-rose-200';
  };

  const filteredCandidates = candidates.filter((c) => {
    const passesScore = c.overall_score >= minScoreFilter;
    const q = searchQuery.toLowerCase();
    const passesQuery =
      !q ||
      c.candidate_name.toLowerCase().includes(q) ||
      c.all_extracted_skills.some((s) => s.toLowerCase().includes(q));
    return passesScore && passesQuery;
  });

  const averageScore = candidates.length
    ? (candidates.reduce((sum, candidate) => sum + candidate.overall_score, 0) / candidates.length).toFixed(1)
    : '—';

  return (
    <div className="min-h-screen flex flex-col bg-[#f7f8fc]">
      {/* Top Navbar */}
      <header className="bg-slate-950 text-white shadow-xl">
        <div className="max-w-7xl mx-auto px-6 py-4 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-400 to-violet-600 flex items-center justify-center text-lg font-black shadow-lg shadow-indigo-950/40">AI</div>
            <div>
              <h1 className="text-lg font-bold tracking-tight">TalentLens</h1>
              <p className="text-xs text-slate-400">AI candidate intelligence workspace</p>
            </div>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <span className="hidden sm:inline text-slate-400">Semantic + structured matching</span>
            <span className="flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-400/30 text-emerald-300 px-3 py-1.5 rounded-full">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span> System ready
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl w-full mx-auto px-6 py-8 space-y-8 flex-1">
        <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-700 via-indigo-600 to-violet-700 px-7 py-8 text-white shadow-xl shadow-indigo-200">
          <div className="relative z-10 max-w-2xl">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-indigo-200 mb-3">Recruiting intelligence</p>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">Find the strongest candidates faster.</h2>
            <p className="mt-3 text-sm sm:text-base text-indigo-100 leading-relaxed">Upload one role and a batch of resumes. TalentLens combines semantic context, normalized skills, and experience fit into a transparent shortlist.</p>
          </div>
          <div className="absolute -right-10 -top-20 h-72 w-72 rounded-full border-[32px] border-white/10"></div>
          <div className="absolute right-24 -bottom-28 h-56 w-56 rounded-full border-[24px] border-white/10"></div>
        </section>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            ['01', 'Add a role', 'Paste or upload the job description'],
            ['02', 'Upload resumes', 'Process 10+ PDF or DOCX files'],
            ['03', 'Review the shortlist', 'Inspect scores and skill gaps'],
          ].map(([number, title, description]) => (
            <div key={number} className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-3 shadow-sm">
              <span className="h-9 w-9 shrink-0 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center text-xs font-bold">{number}</span>
              <div><p className="text-sm font-bold text-slate-800">{title}</p><p className="text-xs text-slate-500 mt-0.5">{description}</p></div>
            </div>
          ))}
        </div>

        {notice && (
          <div className="flex items-center justify-between rounded-xl border border-indigo-100 bg-indigo-50 px-4 py-3 text-sm text-indigo-800">
            <span><strong className="mr-1">Status:</strong>{notice}</span>
            <button type="button" onClick={() => setNotice('')} className="text-indigo-500 hover:text-indigo-800" aria-label="Dismiss status">✕</button>
          </div>
        )}

        {/* Input Grid: Module 1 & Module 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Module 1: Job Description Input */}
          <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-base font-bold text-slate-800">
                  <span className="text-indigo-600 mr-2">01</span>Job Description
                </h2>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => { setJdText(SAMPLE_JD_TEXT); setNotice('Sample Senior Full-Stack Engineer role loaded'); }}
                    className="text-xs font-medium text-indigo-600 hover:text-indigo-800 underline"
                  >
                    Load Sample JD
                  </button>
                  <label className="cursor-pointer text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium px-3 py-1.5 rounded-lg border border-slate-300">
                    Upload JD (.pdf/.docx/.txt)
                    <input
                      type="file"
                      accept=".pdf,.docx,.txt"
                      onChange={handleJdFileUpload}
                      className="hidden"
                    />
                  </label>
                </div>
              </div>

              <textarea
                rows={8}
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Paste the Job Description here or upload a file above..."
                className="w-full rounded-lg border border-slate-300 p-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              />
            </div>

            {parsedJd && (
              <div className="mt-4 pt-4 border-t border-slate-100 text-xs space-y-2">
                <div className="flex flex-wrap gap-4 text-slate-600">
                  <span>
                    <strong className="text-slate-800">Min Experience:</strong>{' '}
                    {parsedJd.min_experience_years > 0
                      ? `${parsedJd.min_experience_years}+ years`
                      : 'Not specified'}
                  </span>
                  <span>
                    <strong className="text-slate-800">Qualification:</strong>{' '}
                    {parsedJd.education_requirement}
                  </span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {parsedJd.required_skills.map((skill) => (
                    <span
                      key={skill}
                      className="px-2 py-0.5 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </section>

          {/* Module 2: Batch Resume Upload */}
          <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-base font-bold text-slate-800">
                  <span className="text-indigo-600 mr-2">02</span>Candidate Resumes
                </h2>
                <span
                  className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${
                    resumeFiles.length >= 10
                      ? 'bg-emerald-100 text-emerald-800'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {resumeFiles.length} file(s) selected
                </span>
              </div>

              <label className="flex flex-col items-center justify-center border-2 border-dashed border-slate-300 hover:border-indigo-400 rounded-xl p-8 cursor-pointer bg-slate-50/60 transition">
                <p className="text-sm font-semibold text-slate-700">
                  Click to select multiple resumes (10+ supported)
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  Supports .PDF and .DOCX formats
                </p>
                <input
                  type="file"
                  multiple
                  accept=".pdf,.docx"
                  onChange={handleResumeSelection}
                  className="hidden"
                />
              </label>

              {resumeFiles.length > 0 && (
                <div className="mt-4 max-h-36 overflow-y-auto border border-slate-200 rounded-lg divide-y divide-slate-100 text-xs">
                  {resumeFiles.map((f, i) => (
                    <div key={i} className="px-3 py-1.5 flex justify-between items-center">
                      <span className="truncate font-medium text-slate-700">{f.name}</span>
                      <span className="text-slate-400 ml-2">
                        {(f.size / 1024).toFixed(1)} KB
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button
              type="button"
              onClick={handleRunMatching}
              disabled={loading}
              className="mt-6 w-full py-3 px-4 bg-slate-950 hover:bg-indigo-700 disabled:bg-indigo-300 text-white font-semibold rounded-xl shadow-lg shadow-slate-200 transition text-sm"
            >
              {loading
                ? 'Analyzing Semantic Embeddings & Ranking Candidates...'
                : 'Analyze & Rank Candidates'}
            </button>
          </section>
        </div>

        {/* Parsing Warnings if any */}
        {errors.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-xs text-amber-800">
            <strong>Skipped {errors.length} file(s):</strong>{' '}
            {errors.map((e) => `${e.filename} (${e.error})`).join(', ')}
          </div>
        )}

        {/* Module 4: Candidate Ranking Dashboard */}
        {candidates.length > 0 && (
          <section className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="grid grid-cols-2 md:grid-cols-4 border-b border-slate-200">
              {[
                ['Candidates analyzed', candidates.length],
                ['Average match', `${averageScore}%`],
                ['Top candidate', candidates[0]?.candidate_name || '—'],
                ['Required skills', parsedJd?.required_skills?.length || 0],
              ].map(([label, value]) => (
                <div key={label} className="p-5 border-r border-slate-100 last:border-r-0">
                  <p className="text-xs text-slate-500">{label}</p>
                  <p className="mt-1 text-xl font-bold text-slate-900 truncate">{value}</p>
                </div>
              ))}
            </div>
            <div className="p-6 border-b border-slate-200 flex flex-wrap items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-bold text-slate-800">
                  Candidate Ranking Dashboard ({filteredCandidates.length} of {candidates.length})
                </h2>
                <p className="text-xs text-slate-500">
                  Click any candidate row to inspect skill gaps, experience fit, and AI score reasoning.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Filter by name or skill..."
                  className="text-xs border border-slate-300 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <select
                  value={minScoreFilter}
                  onChange={(e) => setMinScoreFilter(Number(e.target.value))}
                  className="text-xs border border-slate-300 rounded-lg px-3 py-2 outline-none"
                >
                  <option value={0}>All Scores (0%+)</option>
                  <option value={60}>60%+ Match</option>
                  <option value={75}>75%+ Match</option>
                  <option value={85}>85%+ Match</option>
                </select>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-xs uppercase text-slate-500">
                    <th className="py-3.5 px-4">Rank</th>
                    <th className="py-3.5 px-4">Candidate</th>
                    <th className="py-3.5 px-4">Experience</th>
                    <th className="py-3.5 px-4">Match %</th>
                    <th className="py-3.5 px-4">Score Breakdown</th>
                    <th className="py-3.5 px-4">Matched Skills</th>
                    <th className="py-3.5 px-4 text-right">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-sm">
                  {filteredCandidates.map((cand) => (
                    <tr
                      key={cand.id}
                      onClick={() => setSelectedCandidate(cand)}
                      className="hover:bg-indigo-50/50 cursor-pointer transition"
                    >
                      <td className="py-3.5 px-4 font-bold text-slate-700">
                        #{candidates.findIndex((item) => item.id === cand.id) + 1}
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-slate-900">{cand.candidate_name}</div>
                        <div className="text-xs text-slate-500">{cand.filename}</div>
                      </td>
                      <td className="py-3.5 px-4 text-slate-700 font-medium">
                        {cand.experience_years} yrs
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-block px-2.5 py-1 rounded-full text-xs font-bold border ${getScoreBadgeColor(
                            cand.overall_score
                          )}`}
                        >
                          {cand.overall_score}%
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-600">
                        <div>Semantic: {cand.semantic_score}%</div>
                        <div>Skills: {cand.skill_score}% | Exp: {cand.experience_score}%</div>
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="flex flex-wrap gap-1 max-w-xs">
                          {cand.matched_skills.slice(0, 5).map((skill) => (
                            <span
                              key={skill}
                              className="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded text-xs"
                            >
                              {skill}
                            </span>
                          ))}
                          {cand.matched_skills.length > 5 && (
                            <span className="text-xs text-slate-500 px-1">
                              +{cand.matched_skills.length - 5} more
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          type="button"
                          className="text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                        >
                          Inspect →
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>

      {/* Module 5: Candidate-Level Analysis Modal */}
      {selectedCandidate && (
        <div
          className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedCandidate(null)}
        >
          <div
            className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-slate-200 p-6 space-y-6"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-start justify-between border-b border-slate-100 pb-4">
              <div>
                <h3 className="text-xl font-bold text-slate-900">
                  {selectedCandidate.candidate_name}
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  {selectedCandidate.email} • {selectedCandidate.phone} •{' '}
                  {selectedCandidate.education}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span
                  className={`px-3 py-1 rounded-full text-sm font-bold border ${getScoreBadgeColor(
                    selectedCandidate.overall_score
                  )}`}
                >
                  {selectedCandidate.overall_score}% Match
                </span>
                <button
                  onClick={() => setSelectedCandidate(null)}
                  className="text-slate-400 hover:text-slate-700 text-lg font-bold px-2"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Sub-score Metric Cards */}
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <div className="text-xs text-slate-500">Semantic Similarity (45%)</div>
                <div className="text-lg font-bold text-indigo-700">
                  {selectedCandidate.semantic_score}%
                </div>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <div className="text-xs text-slate-500">Skill Alignment (35%)</div>
                <div className="text-lg font-bold text-emerald-700">
                  {selectedCandidate.skill_score}%
                </div>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <div className="text-xs text-slate-500">Experience Fit (20%)</div>
                <div className="text-lg font-bold text-amber-700">
                  {selectedCandidate.experience_score}%
                </div>
              </div>
            </div>

            {/* Reasons Behind Matching Score */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                AI Score Explanation & Reasoning
              </h4>
              <ul className="space-y-1.5 text-sm text-slate-700 bg-indigo-50/50 p-4 rounded-xl border border-indigo-100">
                {selectedCandidate.reasons.map((reason, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-indigo-600 font-bold">•</span>
                    <span>{reason}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Experience Comparison */}
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-sm flex justify-between items-center">
              <div>
                <span className="text-slate-500">JD Required Experience:</span>{' '}
                <strong className="text-slate-800">
                  {parsedJd?.min_experience_years || 0}+ years
                </strong>
              </div>
              <div>
                <span className="text-slate-500">Candidate Experience:</span>{' '}
                <strong className="text-slate-800">
                  {selectedCandidate.experience_years} years
                </strong>
              </div>
            </div>

            {/* Matched vs Missing Skills */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-700 mb-2">
                  Matched Skills ({selectedCandidate.matched_skills.length})
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {selectedCandidate.matched_skills.length > 0 ? (
                    selectedCandidate.matched_skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-md text-xs font-medium"
                      >
                        {skill}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-slate-400">No direct skill matches</span>
                  )}
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-rose-700 mb-2">
                  Missing Skills ({selectedCandidate.missing_skills.length})
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {selectedCandidate.missing_skills.length > 0 ? (
                    selectedCandidate.missing_skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-2.5 py-1 bg-rose-100 text-rose-800 rounded-md text-xs font-medium"
                      >
                        {skill}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-emerald-600 font-medium">
                      All required skills covered!
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Related / Transferable Skills */}
            {selectedCandidate.related_skills?.length > 0 && (
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-blue-700 mb-2">
                  Semantic / Transferable Skills Detected
                </h4>
                <div className="flex flex-wrap gap-2">
                  {selectedCandidate.related_skills.map((rel, i) => (
                    <span
                      key={i}
                      className="px-2.5 py-1 bg-blue-50 text-blue-800 border border-blue-200 rounded-md text-xs"
                    >
                      Has <strong>{rel.candidate_has}</strong> (matches{' '}
                      <strong>{rel.required}</strong> at {rel.similarity}% similarity)
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Extracted Resume Snippet */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                Extracted Profile Summary
              </h4>
              <p className="text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200 leading-relaxed">
                {selectedCandidate.resume_summary}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}