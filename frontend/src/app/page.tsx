'use client';

import React, { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { 
  LayoutDashboard, Search, Brain, Send, Loader2, 
  Globe, ExternalLink, User, Target, CheckCircle2, Trash2 
} from 'lucide-react';

interface Lead {
  id: string;
  company_name: string;
  region: string;
  category: string;
  status: string;
  email: string;
  website: string;
  profile_url: string;
  source: string;
  created_at: string;
}

const LeadSkeleton = () => (
  <div className="p-5 bg-dubai-slate border border-white/10 rounded-3xl animate-pulse">
    <div className="flex justify-between items-center">
      <div className="space-y-3">
        <div className="h-5 w-40 bg-white/10 rounded-full" />
        <div className="h-3 w-60 bg-white/5 rounded-full" />
      </div>
      <div className="h-8 w-8 bg-white/10 rounded-full" />
    </div>
  </div>
);

const StatusBadge = ({ status }: { status: string }) => {
  const colors: Record<string, string> = {
    'new': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    'analyzed': 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    'offered': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    'sent': 'bg-green-500/20 text-green-400 border-green-500/30',
  };
  const current = colors[status.toLowerCase()] || 'bg-white/10 text-slate-400 border-white/10';
  return <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border ${current}`}>{status}</span>;
};

const LeadCard = ({ lead, isSelected, onClick }: { lead: Lead, isSelected: boolean, onClick: () => void }) => (
  <div 
    onClick={onClick}
    className={`group p-5 bg-dubai-slate border transition-all duration-300 rounded-3xl cursor-pointer ${
      isSelected ? 'border-dubai-gold ring-1 ring-dubai-gold bg-dubai-slate/80 neon-border' : 'border-white/10 hover:border-white/30'
    }`}
  >
    <div className="flex justify-between items-start">
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <h4 className="font-serif font-bold text-white group-hover:text-dubai-gold transition-colors">{lead.company_name}</h4>
          <StatusBadge status={lead.status} />
        </div>
        <p className="text-xs text-slate-400 flex items-center gap-1">
          <Globe className="w-3 h-3" /> {lead.region} • {lead.category}
        </p>
      </div>
      <div className={`p-2 rounded-2xl transition-all ${isSelected ? 'bg-dubai-gold text-dubai-dark' : 'bg-white/5 text-slate-400 group-hover:text-dubai-gold'}`}>
        <Brain className="w-5 h-5" />
      </div>
    </div>
    <div className="mt-4 flex items-center justify-between pt-4 border-t border-white/5">
      <span className="text-[10px] text-slate-500 uppercase font-medium">{lead.source}</span>
      <div className={`w-4 h-4 transition-all ${isSelected ? 'text-dubai-gold' : 'text-slate-500'}`}>
        <div className="w-full h-full border-t-2 border-r-2 border-current rotate-45 translate-x-1 translate-y-1" />
      </div>
    </div>
  </div>
);

const Dashboard = () => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState({ keyword: '', region: '' });
  const [isSearching, setIsSearching] = useState(false);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [analysis, setAnalysis] = useState<string | null>(null);
  const [offer, setOffer] = useState<{ua: string, en: string} | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    fetchLeads();
    const logInterval = setInterval(fetchLogs, 3000);
    return () => clearInterval(logInterval);
  }, []);

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const { data } = await supabase.from('leads').select('*').order('created_at', { ascending: false });
      setLeads(data || []);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch('http://localhost:8000/logs');
      const data = await res.json();
      if (data.logs) setLogs(data.logs);
    } catch (e) { console.error('Logs error:', e); }
  };

  const handleSearch = async () => {
    setIsSearching(true);
    try {
      const res = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchQuery),
      });
      const result = await res.json();
      if (result.status === 'success') {
        setLeads(prev => [...result.data, ...prev]);
      }
    } catch (e) { alert('Server Error'); } finally { setIsSearching(false); }
  };

  const runAnalysis = async (leadId: string) => {
    setIsAnalyzing(true); setAnalysis(null); setOffer(null);
    try {
      const res = await fetch(`http://localhost:8000/analyze/${leadId}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setAnalysis(typeof data.analysis === 'object' ? data.analysis.analysis : data.analysis);
    } catch (e: any) { alert(e.message); } finally { setIsAnalyzing(false); }
  };

  const generateOffer = async (leadId: string) => {
    setIsGenerating(true);
    try {
      const res = await fetch(`http://localhost:8000/generate-offer/${leadId}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setOffer({ ua: data.offer.ua, en: data.offer.en });
    } catch (e: any) { alert(e.message); } finally { setIsGenerating(false); }
  };

  const sendOffer = async (leadId: string) => {
    setIsSending(true);
    try {
      const res = await fetch(`http://localhost:8000/send/${leadId}`, { method: 'POST' });
      const data = await res.json();
      if (data.status === 'error') throw new Error(data.message);
      alert('Offer sent successfully!');
    } catch (e: any) { alert(e.message); } finally { setIsSending(false); }
  };

  const deleteLead = async (id: string) => {
    if (!confirm('Delete this lead?')) return;
    try {
      await fetch(`http://localhost:8000/leads/${id}`, { method: 'DELETE' });
      setLeads(leads.filter(l => l.id !== id));
      setSelectedLead(null);
      setAnalysis(null);
      setOffer(null);
    } catch (e) { alert('Deletion error'); }
  };

  return (
    <div className="flex h-screen bg-dubai-dark text-white overflow-hidden font-sans pt-20">
      <aside className="w-72 bg-dubai-slate border-r border-white/5 hidden lg:flex flex-col p-6">
        <div className="mb-10">
          <div className="flex items-center gap-3 text-dubai-gold mb-2">
            <Target className="w-5 h-5" />
            <span className="text-xs uppercase tracking-widest font-bold">Core Engine</span>
          </div>
          <h2 className="text-2xl font-serif font-bold">Control</h2>
        </div>
        <nav className="flex-1 space-y-2">
          <button className="w-full flex items-center space-x-3 p-4 bg-dubai-gold text-dubai-dark rounded-2xl font-bold transition-all shadow-lg shadow-dubai-gold/20">
            <LayoutDashboard className="w-5 h-5" /> <span>Dashboard</span>
          </button>
        </nav>
        <div className="mt-auto pt-6 border-t border-white/5">
          <div className="bg-dubai-dark p-4 rounded-2xl border border-white/5">
            <div className="flex items-center gap-2 text-xs text-slate-500 mb-3">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span>System Active</span>
            </div>
            <p className="text-[10px] text-slate-600 leading-relaxed">Version 3.0.0 • Pure Maps Edition</p>
          </div>
        </div>
      </aside>

      <main className="flex-1 flex h-full p-6 md:p-10 gap-8 overflow-hidden">
        <div className="flex-1 overflow-y-auto pr-4 space-y-10">
          <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-6">
            <div>
              <h1 className="text-4xl font-serif font-bold mb-2">Client Acquisition</h1>
              <p className="text-slate-400 flex items-center gap-2">
                AI Lead Generation System <span className="w-1 h-1 bg-slate-600 rounded-full" /> AlexRV-Dev
              </p>
            </div>
          </header>

          <div className="grid grid-cols-1 xl:grid-cols-12 gap-10">
            <div className="xl:col-span-4 space-y-8">
              <div className="bg-dubai-slate p-8 rounded-3xl border border-white/10 relative overflow-hidden neon-border">
                <h3 className="text-xl font-serif font-bold mb-6 flex items-center gap-2">
                  <Search className="w-5 h-5 text-dubai-gold" /> Search (Google Maps)
                </h3>
                <div className="space-y-5">
                  <div className="space-y-2">
                    <label className="text-[10px] uppercase tracking-widest text-slate-500 font-bold ml-1">Niche</label>
                    <input placeholder="Luxury Hotel..." className="w-full bg-dubai-dark border border-white/10 p-4 rounded-2xl outline-none focus:ring-2 focus:ring-dubai-gold transition-all text-sm" onChange={(e) => setSearchQuery({...searchQuery, keyword: e.target.value})} />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] uppercase tracking-widest text-slate-500 font-bold ml-1">Region</label>
                    <input placeholder="Dubai, UAE..." className="w-full bg-dubai-dark border border-white/10 p-4 rounded-2xl outline-none focus:ring-2 focus:ring-dubai-gold transition-all text-sm" onChange={(e) => setSearchQuery({...searchQuery, region: e.target.value})} />
                  </div>
                  <button onClick={handleSearch} disabled={isSearching} className="w-full bg-dubai-gold text-dubai-dark font-bold py-4 rounded-2xl hover:bg-dubai-goldLight transition-all flex items-center justify-center gap-2 shadow-xl shadow-dubai-gold/20 neon-button">
                    {isSearching ? <Loader2 className="animate-spin w-5 h-5" /> : <Search className="w-5 h-5" />} {isSearching ? 'Searching...' : 'Find Leads'}
                  </button>
                </div>
              </div>
              <div className="bg-dubai-dark border border-white/10 rounded-3xl p-8 relative overflow-hidden">
                <h3 className="text-xs uppercase tracking-widest text-slate-500 mb-6 font-bold flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-dubai-gold rounded-full" /> Live Logs
                </h3>
                <div className="space-y-3">
                  {logs.map((log, i) => (
                    <React.Fragment key={i}>
                      <div className="text-[11px] text-slate-400 border-l border-dubai-gold/30 pl-3 py-1 animate-fade-in font-mono">
                        {log}
                      </div>
                      {i === logs.length - 1 && <div className="h-1 w-full bg-dubai-gold/20 animate-pulse rounded-full" />}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            </div>
            <div className="xl:col-span-8 space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-2xl font-serif font-bold">Golden Leads</h3>
                <span className="text-xs text-slate-500 font-medium">{leads.length} found</span>
              </div>
              {loading ? (
                <div className="grid grid-cols-1 gap-4">{[1, 2, 3, 4, 5].map(i => <LeadSkeleton key={i} />)}</div>
              ) : (
                <div className="grid grid-cols-1 gap-4">
                  {leads.map(lead => (
                    <LeadCard key={lead.id} lead={lead} isSelected={selectedLead?.id === lead.id} onClick={() => setSelectedLead(lead)} />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="hidden xl:block w-[450px] overflow-y-auto h-full pr-2">
          {selectedLead ? (
            <div className="bg-dubai-slate border border-white/10 rounded-3xl p-8 shadow-2xl neon-border">
              <div className="flex justify-between items-start mb-8">
                <div>
                  <h3 className="text-2xl font-serif font-bold text-white">{selectedLead.company_name}</h3>
                  <p className="text-xs text-slate-400 uppercase tracking-widest mt-1">{selectedLead.region}</p>
                </div>
                <button onClick={() => deleteLead(selectedLead.id)} className="p-3 bg-red-500/10 hover:bg-red-500/20 text-red-500 rounded-2xl transition-all">
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
              <div className="space-y-4">
                <button onClick={() => runAnalysis(selectedLead.id)} disabled={isAnalyzing} className="w-full py-4 bg-white/10 hover:bg-white/20 rounded-2xl font-bold transition-all flex items-center justify-center gap-3 border border-white/5">
                  {isAnalyzing ? <Loader2 className="animate-spin w-5 h-5" /> : <Brain className="w-5 h-5 text-dubai-gold" />}
                  {isAnalyzing ? 'AI Analyzing...' : 'Analyze Business'}
                </button>
                <div className="grid grid-cols-2 gap-3">
                  {selectedLead.website && (
                    <a href={selectedLead.website} target="_blank" rel="noopener noreferrer" className="py-3 bg-dubai-gold/10 hover:bg-dubai-gold/20 text-dubai-gold border border-dubai-gold/20 rounded-2xl font-medium transition-all flex items-center justify-center gap-2 text-sm">
                      <Globe className="w-4 h-4" /> Website
                    </a>
                  )}
                  {selectedLead.profile_url && (
                    <a href={selectedLead.profile_url} target="_blank" rel="noopener noreferrer" className="py-3 bg-white/5 hover:bg-white/10 text-white border border-white/10 rounded-2xl font-medium transition-all flex items-center justify-center gap-2 text-sm">
                      <ExternalLink className="w-4 h-4" /> Profile
                    </a>
                  )}
                </div>
              </div>
              {analysis && (
                <div className="mt-8 p-6 bg-dubai-dark rounded-3xl border border-white/5 relative group">
                  <div className="absolute -top-3 left-6 px-3 py-1 bg-dubai-gold text-dubai-dark text-[10px] uppercase font-bold rounded-full">AI-Diagnosis</div>
                  <div className="space-y-4 mt-2">
                    <div className="p-3 bg-white/5 rounded-xl border-l-2 border-slate-500">
                      <label className="text-[10px] text-slate-500 uppercase font-bold block mb-1">Internal (UA)</label>
                      <p className="text-sm text-slate-300 italic leading-relaxed">{analysis.split('EN:')[0].replace('UA:', '').trim()}</p>
                    </div>
                    <div className="p-3 bg-dubai-gold/5 rounded-xl border-l-2 border-dubai-gold">
                      <label className="text-[10px] text-dubai-gold uppercase font-bold block mb-1">Client (EN)</label>
                      <p className="text-sm text-white leading-relaxed">{analysis.split('EN:')[1] || 'Analysis in English not generated'}</p>
                    </div>
                  </div>
                  <button onClick={() => generateOffer(selectedLead.id)} disabled={isGenerating} className="w-full mt-6 py-3 bg-dubai-gold text-dubai-dark rounded-xl font-bold text-sm flex items-center justify-center gap-2 hover:bg-dubai-goldLight transition-all neon-button">
                    {isGenerating ? <Loader2 className="animate-spin w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
                    {isGenerating ? 'Generating...' : 'Create Offer'}
                  </button>
                </div>
              )}
              {offer && (
                <div className="mt-8 p-6 bg-dubai-dark rounded-3xl border border-white/5 relative">
                <div className="absolute -top-3 left-6 px-3 py-1 bg-white text-dubai-dark text-[10px] uppercase font-bold rounded-full">Final Offer</div>
                <div className="space-y-6 mt-2">
                  <div>
                    <label className="text-[10px] text-slate-500 uppercase font-bold block mb-2 ml-1">Internal (UA)</label>
                    <textarea value={offer.ua} onChange={(e) => setOffer({...offer, ua: e.target.value})} className="w-full bg-dubai-slate/50 border border-white/5 p-4 rounded-2xl text-xs text-slate-400 outline-none resize-none h-24 focus:ring-1 focus:ring-dubai-gold transition-all" />
                  </div>
                  <div>
                    <label className="text-[10px] text-dubai-gold uppercase font-bold block mb-2 ml-1">Client (EN)</label>
                    <textarea value={offer.en} onChange={(e) => setOffer({...offer, en: e.target.value})} className="w-full bg-dubai-slate/50 border border-white/5 p-4 rounded-2xl text-sm text-white outline-none resize-none h-32 focus:ring-1 focus:ring-dubai-gold transition-all" />
                  </div>
                </div>
                <div className="grid grid-cols-1 gap-3 mt-8">
                  <button onClick={() => sendOffer(selectedLead.id)} disabled={isSending} className="w-full py-4 bg-white/10 hover:bg-white/20 text-white rounded-2xl font-bold text-sm flex items-center justify-center gap-3 transition-all border border-white/5">
                    {isSending ? <Loader2 className="animate-spin w-4 h-4" /> : <Send className="w-4 h-4 text-dubai-gold" />} Send Email Offer
                  </button>
                </div>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center py-20 bg-dubai-slate/30 border border-dashed border-white/10 rounded-3xl text-slate-500">
              <div className="p-4 bg-white/5 rounded-full mb-4"><User className="w-8 h-8 opacity-20" /></div>
              <p className="max-w-xs mx-auto italic">Select a lead from the list for detailed analysis and acquisition strategy</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
