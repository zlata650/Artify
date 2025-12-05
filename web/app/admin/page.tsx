'use client'

import { useState, useEffect } from 'react'

// Types
interface DataSource {
  id: string
  name: string
  url: string
  filter_keyword: string
  enabled: boolean
}

interface Stats {
  period: string
  total_concerts: number
  new_concerts: number
  sources_parsed: number
  parsing_errors: number
}

interface ParsingResult {
  source_id: string
  source_name: string
  concerts_found: number
  concerts_added: number
  duration: number
  status: string
  error?: string
}

interface HistoryItem {
  id: number
  source_id: string
  source_name: string
  timestamp: string
  concerts_found: number
  concerts_added: number
  duration: number
  status: string
  error?: string
}

interface ChartData {
  date: string
  new_concerts: number
  errors: number
}

export default function AdminDashboard() {
  // États
  const [sources, setSources] = useState<DataSource[]>([])
  const [stats, setStats] = useState<{
    today: Stats | null
    week: Stats | null
    month: Stats | null
  }>({ today: null, week: null, month: null })
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [chartData, setChartData] = useState<ChartData[]>([])
  const [schedulerStatus, setSchedulerStatus] = useState({ running: false, jobs: [] as string[] })
  const [loading, setLoading] = useState(true)
  const [parsing, setParsing] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'sources' | 'history' | 'scheduler'>('overview')
  const [notification, setNotification] = useState<{ type: 'success' | 'error', message: string } | null>(null)

  // Charger les données au démarrage
  useEffect(() => {
    loadAllData()
  }, [])

  // Effacer la notification après 5 secondes
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000)
      return () => clearTimeout(timer)
    }
  }, [notification])

  const loadAllData = async () => {
    setLoading(true)
    try {
      await Promise.all([
        loadSources(),
        loadStats(),
        loadHistory(),
        loadSchedulerStatus()
      ])
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadSources = async () => {
    try {
      const res = await fetch('/api/admin/sources')
      const data = await res.json()
      setSources(data.sources || [])
    } catch (error) {
      console.error('Error loading sources:', error)
    }
  }

  const loadStats = async () => {
    try {
      const res = await fetch('/api/admin/stats')
      const data = await res.json()
      setStats({
        today: data.today,
        week: data.week,
        month: data.month
      })
    } catch (error) {
      console.error('Error loading stats:', error)
    }
  }

  const loadHistory = async () => {
    try {
      const res = await fetch('/api/admin/history?limit=20')
      const data = await res.json()
      setHistory(data.history || [])
    } catch (error) {
      console.error('Error loading history:', error)
    }
  }

  const loadSchedulerStatus = async () => {
    try {
      const res = await fetch('/api/admin/scheduler')
      const data = await res.json()
      setSchedulerStatus(data)
    } catch (error) {
      console.error('Error loading scheduler status:', error)
    }
  }

  const triggerParsing = async (sourceId?: string) => {
    setParsing(true)
    try {
      const res = await fetch('/api/admin/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sourceId ? { source_id: sourceId } : {})
      })
      const data = await res.json()
      
      if (data.success) {
        const totalAdded = data.results?.reduce((acc: number, r: ParsingResult) => acc + r.concerts_added, 0) || 0
        setNotification({
          type: 'success',
          message: `✅ Parsing terminé ! ${totalAdded} nouveaux concerts ajoutés.`
        })
        await loadAllData()
      } else {
        setNotification({
          type: 'error',
          message: data.error || 'Erreur lors du parsing'
        })
      }
    } catch (error) {
      setNotification({
        type: 'error',
        message: "❌ Erreur: L'API Admin n'est pas disponible. Lancez-la avec: python admin_api.py"
      })
    } finally {
      setParsing(false)
    }
  }

  const toggleScheduler = async (action: 'start' | 'stop') => {
    try {
      const res = await fetch(`/api/admin/scheduler?action=${action}`, { method: 'POST' })
      const data = await res.json()
      
      if (data.success) {
        setNotification({
          type: 'success',
          message: action === 'start' ? '▶️ Scheduler démarré' : '⏹️ Scheduler arrêté'
        })
        await loadSchedulerStatus()
      } else {
        setNotification({
          type: 'error',
          message: data.error || `Erreur lors de ${action === 'start' ? 'démarrage' : "l'arrêt"} du scheduler`
        })
      }
    } catch (error) {
      setNotification({
        type: 'error',
        message: "❌ Erreur de connexion à l'API"
      })
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.spinner}></div>
        <p style={styles.loadingText}>Chargement du dashboard...</p>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <div style={styles.logoSection}>
            <span style={styles.logo}>🎭</span>
            <h1 style={styles.title}>Artify Admin</h1>
          </div>
          <div style={styles.headerActions}>
            <button
              onClick={() => loadAllData()}
              style={styles.refreshBtn}
              title="Rafraîchir"
            >
              🔄
            </button>
            <a href="/" style={styles.backLink}>← Retour au site</a>
          </div>
        </div>
      </header>

      {/* Notification */}
      {notification && (
        <div style={{
          ...styles.notification,
          backgroundColor: notification.type === 'success' ? '#10b981' : '#ef4444'
        }}>
          {notification.message}
        </div>
      )}

      {/* Navigation */}
      <nav style={styles.nav}>
        {(['overview', 'sources', 'history', 'scheduler'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              ...styles.navBtn,
              ...(activeTab === tab ? styles.navBtnActive : {})
            }}
          >
            {tab === 'overview' && '📊 Vue d\'ensemble'}
            {tab === 'sources' && '🌐 Sources'}
            {tab === 'history' && '📜 Historique'}
            {tab === 'scheduler' && '⏰ Planification'}
          </button>
        ))}
      </nav>

      {/* Content */}
      <main style={styles.main}>
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div style={styles.overviewGrid}>
            {/* Quick Action Card */}
            <div style={styles.actionCard}>
              <h2 style={styles.cardTitle}>⚡ Action rapide</h2>
              <p style={styles.cardDesc}>
                Lancez le parsing de toutes les sources actives
              </p>
              <button
                onClick={() => triggerParsing()}
                disabled={parsing}
                style={{
                  ...styles.primaryBtn,
                  opacity: parsing ? 0.7 : 1
                }}
              >
                {parsing ? (
                  <>
                    <span style={styles.spinnerSmall}></span>
                    Parsing en cours...
                  </>
                ) : (
                  '🚀 Lancer le parsing'
                )}
              </button>
            </div>

            {/* Stats Cards */}
            <div style={styles.statsGrid}>
              <StatCard
                icon="📅"
                title="Aujourd'hui"
                value={stats.today?.new_concerts || 0}
                label="nouveaux concerts"
                sublabel={`${stats.today?.sources_parsed || 0} sources parsées`}
                color="#3b82f6"
              />
              <StatCard
                icon="📆"
                title="Cette semaine"
                value={stats.week?.new_concerts || 0}
                label="nouveaux concerts"
                sublabel={`${stats.week?.parsing_errors || 0} erreurs`}
                color="#8b5cf6"
              />
              <StatCard
                icon="📊"
                title="Ce mois"
                value={stats.month?.new_concerts || 0}
                label="nouveaux concerts"
                sublabel={`${stats.month?.sources_parsed || 0} parsings`}
                color="#06b6d4"
              />
              <StatCard
                icon="🎵"
                title="Total BDD"
                value={stats.today?.total_concerts || 0}
                label="concerts"
                sublabel="dans la base"
                color="#10b981"
              />
            </div>

            {/* Scheduler Status */}
            <div style={styles.schedulerCard}>
              <div style={styles.schedulerHeader}>
                <h3 style={styles.schedulerTitle}>
                  <span style={{
                    ...styles.statusDot,
                    backgroundColor: schedulerStatus.running ? '#10b981' : '#ef4444'
                  }}></span>
                  Scheduler: {schedulerStatus.running ? 'Actif' : 'Inactif'}
                </h3>
                <button
                  onClick={() => toggleScheduler(schedulerStatus.running ? 'stop' : 'start')}
                  style={schedulerStatus.running ? styles.stopBtn : styles.startBtn}
                >
                  {schedulerStatus.running ? '⏹️ Arrêter' : '▶️ Démarrer'}
                </button>
              </div>
              {schedulerStatus.jobs.length > 0 && (
                <div style={styles.jobsList}>
                  <p style={styles.jobsTitle}>Tâches planifiées:</p>
                  {schedulerStatus.jobs.map((job, i) => (
                    <p key={i} style={styles.jobItem}>{job}</p>
                  ))}
                </div>
              )}
            </div>

            {/* Recent Activity */}
            <div style={styles.recentCard}>
              <h3 style={styles.recentTitle}>🕐 Activité récente</h3>
              <div style={styles.activityList}>
                {history.slice(0, 5).map(item => (
                  <div key={item.id} style={styles.activityItem}>
                    <span style={{
                      ...styles.activityStatus,
                      backgroundColor: item.status === 'success' ? '#10b981' : '#ef4444'
                    }}>
                      {item.status === 'success' ? '✓' : '✗'}
                    </span>
                    <div style={styles.activityInfo}>
                      <span style={styles.activitySource}>{item.source_name}</span>
                      <span style={styles.activityMeta}>
                        +{item.concerts_added} concerts • {item.duration.toFixed(1)}s
                      </span>
                    </div>
                    <span style={styles.activityTime}>
                      {formatDate(item.timestamp)}
                    </span>
                  </div>
                ))}
                {history.length === 0 && (
                  <p style={styles.noData}>Aucune activité récente</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Sources Tab */}
        {activeTab === 'sources' && (
          <div style={styles.sourcesContainer}>
            <h2 style={styles.sectionTitle}>🌐 Sources de données</h2>
            <div style={styles.sourcesGrid}>
              {sources.map(source => (
                <div key={source.id} style={styles.sourceCard}>
                  <div style={styles.sourceHeader}>
                    <span style={{
                      ...styles.sourceStatus,
                      backgroundColor: source.enabled ? '#10b981' : '#6b7280'
                    }}>
                      {source.enabled ? 'Actif' : 'Inactif'}
                    </span>
                    <h3 style={styles.sourceName}>{source.name}</h3>
                  </div>
                  <p style={styles.sourceUrl}>{source.url}</p>
                  <p style={styles.sourceKeyword}>
                    Filtre: <code style={styles.code}>{source.filter_keyword}</code>
                  </p>
                  <div style={styles.sourceActions}>
                    <button
                      onClick={() => triggerParsing(source.id)}
                      disabled={parsing}
                      style={styles.parseBtn}
                    >
                      {parsing ? '⏳' : '🔄'} Parser
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div style={styles.historyContainer}>
            <h2 style={styles.sectionTitle}>📜 Historique des parsings</h2>
            <div style={styles.historyTable}>
              <div style={styles.tableHeader}>
                <span style={styles.thDate}>Date</span>
                <span style={styles.thSource}>Source</span>
                <span style={styles.thFound}>Trouvés</span>
                <span style={styles.thAdded}>Ajoutés</span>
                <span style={styles.thDuration}>Durée</span>
                <span style={styles.thStatus}>Statut</span>
              </div>
              {history.map(item => (
                <div key={item.id} style={styles.tableRow}>
                  <span style={styles.tdDate}>{formatDate(item.timestamp)}</span>
                  <span style={styles.tdSource}>{item.source_name}</span>
                  <span style={styles.tdFound}>{item.concerts_found}</span>
                  <span style={styles.tdAdded}>+{item.concerts_added}</span>
                  <span style={styles.tdDuration}>{item.duration.toFixed(1)}s</span>
                  <span style={{
                    ...styles.tdStatus,
                    color: item.status === 'success' ? '#10b981' : '#ef4444'
                  }}>
                    {item.status === 'success' ? '✓ Succès' : '✗ Erreur'}
                  </span>
                </div>
              ))}
              {history.length === 0 && (
                <div style={styles.noDataRow}>
                  <p>Aucun historique disponible</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Scheduler Tab */}
        {activeTab === 'scheduler' && (
          <div style={styles.schedulerContainer}>
            <h2 style={styles.sectionTitle}>⏰ Planification des tâches</h2>
            
            <div style={styles.schedulerGrid}>
              {/* Status Card */}
              <div style={styles.scheduleCard}>
                <h3 style={styles.scheduleCardTitle}>État du Scheduler</h3>
                <div style={styles.scheduleStatus}>
                  <span style={{
                    ...styles.bigStatusDot,
                    backgroundColor: schedulerStatus.running ? '#10b981' : '#ef4444'
                  }}></span>
                  <span style={styles.statusText}>
                    {schedulerStatus.running ? 'En cours d\'exécution' : 'Arrêté'}
                  </span>
                </div>
                <button
                  onClick={() => toggleScheduler(schedulerStatus.running ? 'stop' : 'start')}
                  style={schedulerStatus.running ? styles.bigStopBtn : styles.bigStartBtn}
                >
                  {schedulerStatus.running ? '⏹️ Arrêter le scheduler' : '▶️ Démarrer le scheduler'}
                </button>
              </div>

              {/* Schedule Info */}
              <div style={styles.scheduleCard}>
                <h3 style={styles.scheduleCardTitle}>Tâches programmées</h3>
                <div style={styles.scheduleList}>
                  <div style={styles.scheduleItem}>
                    <span style={styles.scheduleIcon}>🌅</span>
                    <div style={styles.scheduleInfo}>
                      <span style={styles.scheduleName}>Parsing quotidien</span>
                      <span style={styles.scheduleTime}>Tous les jours à 06:00</span>
                    </div>
                  </div>
                  <div style={styles.scheduleItem}>
                    <span style={styles.scheduleIcon}>📅</span>
                    <div style={styles.scheduleInfo}>
                      <span style={styles.scheduleName}>Parsing hebdomadaire</span>
                      <span style={styles.scheduleTime}>Dimanche à 00:00</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Manual Trigger */}
              <div style={styles.scheduleCard}>
                <h3 style={styles.scheduleCardTitle}>Exécution manuelle</h3>
                <p style={styles.scheduleDesc}>
                  Lancez le parsing manuellement sans attendre les tâches planifiées.
                </p>
                <button
                  onClick={() => triggerParsing()}
                  disabled={parsing}
                  style={{
                    ...styles.manualBtn,
                    opacity: parsing ? 0.7 : 1
                  }}
                >
                  {parsing ? '⏳ En cours...' : '🚀 Lancer maintenant'}
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={styles.footer}>
        <p>Artify Admin Dashboard • {new Date().getFullYear()}</p>
      </footer>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  )
}

// Composant StatCard
function StatCard({ icon, title, value, label, sublabel, color }: {
  icon: string
  title: string
  value: number
  label: string
  sublabel: string
  color: string
}) {
  return (
    <div style={{
      ...styles.statCard,
      borderLeft: `4px solid ${color}`
    }}>
      <div style={styles.statHeader}>
        <span style={styles.statIcon}>{icon}</span>
        <span style={styles.statTitle}>{title}</span>
      </div>
      <div style={styles.statValue}>{value.toLocaleString()}</div>
      <div style={styles.statLabel}>{label}</div>
      <div style={styles.statSublabel}>{sublabel}</div>
    </div>
  )
}

// Styles
const styles: { [key: string]: React.CSSProperties } = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#0f0f0f',
    color: '#e5e5e5',
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
  },
  loadingContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    backgroundColor: '#0f0f0f',
  },
  spinner: {
    width: '48px',
    height: '48px',
    border: '3px solid #333',
    borderTopColor: '#f59e0b',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  spinnerSmall: {
    display: 'inline-block',
    width: '16px',
    height: '16px',
    border: '2px solid rgba(255,255,255,0.3)',
    borderTopColor: '#fff',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    marginRight: '8px',
  },
  loadingText: {
    marginTop: '16px',
    color: '#737373',
  },
  header: {
    backgroundColor: '#171717',
    borderBottom: '1px solid #262626',
    padding: '16px 24px',
    position: 'sticky' as const,
    top: 0,
    zIndex: 100,
  },
  headerContent: {
    maxWidth: '1400px',
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logoSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  logo: {
    fontSize: '28px',
  },
  title: {
    fontSize: '20px',
    fontWeight: 700,
    color: '#f59e0b',
    margin: 0,
  },
  headerActions: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  refreshBtn: {
    background: 'none',
    border: '1px solid #333',
    borderRadius: '8px',
    padding: '8px 12px',
    cursor: 'pointer',
    fontSize: '16px',
    transition: 'all 0.2s',
  },
  backLink: {
    color: '#737373',
    fontSize: '14px',
    textDecoration: 'none',
  },
  notification: {
    padding: '12px 24px',
    textAlign: 'center' as const,
    animation: 'fadeIn 0.3s ease',
    color: '#fff',
    fontWeight: 500,
  },
  nav: {
    display: 'flex',
    gap: '4px',
    padding: '16px 24px',
    backgroundColor: '#171717',
    borderBottom: '1px solid #262626',
    maxWidth: '1400px',
    margin: '0 auto',
  },
  navBtn: {
    padding: '10px 20px',
    border: 'none',
    background: 'transparent',
    color: '#737373',
    cursor: 'pointer',
    borderRadius: '8px',
    fontSize: '14px',
    transition: 'all 0.2s',
    fontFamily: 'inherit',
  },
  navBtnActive: {
    backgroundColor: '#262626',
    color: '#f59e0b',
  },
  main: {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: '24px',
  },
  overviewGrid: {
    display: 'grid',
    gap: '24px',
  },
  actionCard: {
    backgroundColor: '#171717',
    border: '1px solid #262626',
    borderRadius: '12px',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    textAlign: 'center' as const,
  },
  cardTitle: {
    fontSize: '18px',
    fontWeight: 600,
    marginBottom: '8px',
    color: '#f5f5f5',
  },
  cardDesc: {
    color: '#737373',
    marginBottom: '20px',
  },
  primaryBtn: {
    backgroundColor: '#f59e0b',
    color: '#0f0f0f',
    border: 'none',
    padding: '14px 32px',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 600,
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    transition: 'all 0.2s',
    fontFamily: 'inherit',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
  },
  statCard: {
    backgroundColor: '#171717',
    border: '1px solid #262626',
    borderRadius: '12px',
    padding: '20px',
  },
  statHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '12px',
  },
  statIcon: {
    fontSize: '20px',
  },
  statTitle: {
    fontSize: '12px',
    color: '#737373',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
  },
  statValue: {
    fontSize: '32px',
    fontWeight: 700,
    color: '#f5f5f5',
    lineHeight: 1,
  },
  statLabel: {
    fontSize: '14px',
    color: '#a3a3a3',
    marginTop: '4px',
  },
  statSublabel: {
    fontSize: '12px',
    color: '#525252',
    marginTop: '8px',
  },
  schedulerCard: {
    backgroundColor: '#171717',
    border: '1px solid #262626',
    borderRadius: '12px',
    padding: '20px',
  },
  schedulerHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  schedulerTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    fontSize: '16px',
    margin: 0,
  },
  statusDot: {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
    display: 'inline-block',
  },
  startBtn: {
    backgroundColor: '#10b981',
    color: '#fff',
    border: 'none',
    padding: '8px 16px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    fontFamily: 'inherit',
  },
  stopBtn: {
    backgroundColor: '#ef4444',
    color: '#fff',
    border: 'none',
    padding: '8px 16px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    fontFamily: 'inherit',
  },
  jobsList: {
    marginTop: '16px',
    paddingTop: '16px',
    borderTop: '1px solid #262626',
  },
  jobsTitle: {
    fontSize: '12px',
    color: '#737373',
    marginBottom: '8px',
  },
  jobItem: {
    fontSize: '13px',
    color: '#a3a3a3',
    padding: '4px 0',
  },
  recentCard: {
    backgroundColor: '#171717',
    border: '1px solid #262626',
    borderRadius: '12px',
    padding: '20px',
  },
  recentTitle: {
    fontSize: '16px',
    marginBottom: '16px',
    color: '#f5f5f5',
  },
  activityList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '12px',
  },
  activityItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px',
    backgroundColor: '#1f1f1f',
    borderRadius: '8px',
  },
  activityStatus: {
    width: '28px',
    height: '28px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#fff',
    fontSize: '14px',
    fontWeight: 600,
  },
  activityInfo: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column' as const,
  },
  activitySource: {
    fontWeight: 500,
    color: '#e5e5e5',
  },
  activityMeta: {
    fontSize: '12px',
    color: '#737373',
  },
  activityTime: {
    fontSize: '12px',
    color: '#525252',
  },
  noData: {
    color: '#525252',
    textAlign: 'center' as const,
    padding: '20px',
  },
  sourcesContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '24px',
  },
  sectionTitle: {
    fontSize: '20px',
    fontWeight: 600,
    color: '#f5f5f5',
    marginBottom: '8px',
  },
  sourcesGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '16px',
  },
  sourceCard: {
    backgroundColor: '#171717',
    border: '1px solid #262626',
    borderRadius: '12px',
    padding: '20px',
  },
  sourceHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '12px',
  },
  sourceStatus: {
    fontSize: '11px',
    padding: '4px 8px',
    borderRadius: '4px',
    color: '#fff',
    fontWeight: 500,
  },
  sourceName: {
    fontSize: '16px',
    fontWeight: 600,
    color: '#f5f5f5',
    margin: 0,
  },
  sourceUrl: {
    fontSize: '13px',
    color: '#525252',
    marginBottom: '8px',
    wordBreak: 'break-all' as const,
  },
  sourceKeyword: {
    fontSize: '13px',
    color: '#737373',
    marginBottom: '16px',
  },
  code: {
    backgroundColor: '#262626',
    padding: '2px 6px',
    borderRadius: '4px',
    fontFamily: 'inherit',
  },
  sourceActions: {
    display: 'flex',
    gap: '8px',
  },
  parseBtn: {
    backgroundColor: '#262626',
    color: '#e5e5e5',
    border: 'none',
    padding: '8px 16px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
    fontFamily: 'inherit',
  },
  historyContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '24px',
  },
  historyTable: {
    backgroundColor: '#171717',
    border: '1px solid #262626',
    borderRadius: '12px',
    overflow: 'hidden',
  },
  tableHeader: {
    display: 'grid',
    gridTemplateColumns: '180px 1fr 80px 80px 80px 100px',
    padding: '14px 20px',
    backgroundColor: '#1f1f1f',
    borderBottom: '1px solid #262626',
    fontSize: '12px',
    color: '#737373',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
  },
  thDate: {},
  thSource: {},
  thFound: { textAlign: 'center' as const },
  thAdded: { textAlign: 'center' as const },
  thDuration: { textAlign: 'center' as const },
  thStatus: { textAlign: 'right' as const },
  tableRow: {
    display: 'grid',
    gridTemplateColumns: '180px 1fr 80px 80px 80px 100px',
    padding: '14px 20px',
    borderBottom: '1px solid #262626',
    alignItems: 'center',
    fontSize: '14px',
  },
  tdDate: { color: '#737373' },
  tdSource: { fontWeight: 500 },
  tdFound: { textAlign: 'center' as const, color: '#a3a3a3' },
  tdAdded: { textAlign: 'center' as const, color: '#10b981', fontWeight: 500 },
  tdDuration: { textAlign: 'center' as const, color: '#737373' },
  tdStatus: { textAlign: 'right' as const, fontWeight: 500 },
  noDataRow: {
    padding: '40px',
    textAlign: 'center' as const,
    color: '#525252',
  },
  schedulerContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '24px',
  },
  schedulerGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '20px',
  },
  scheduleCard: {
    backgroundColor: '#171717',
    border: '1px solid #262626',
    borderRadius: '12px',
    padding: '24px',
  },
  scheduleCardTitle: {
    fontSize: '16px',
    fontWeight: 600,
    color: '#f5f5f5',
    marginBottom: '16px',
  },
  scheduleStatus: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '20px',
  },
  bigStatusDot: {
    width: '16px',
    height: '16px',
    borderRadius: '50%',
  },
  statusText: {
    fontSize: '18px',
    fontWeight: 500,
  },
  bigStartBtn: {
    width: '100%',
    backgroundColor: '#10b981',
    color: '#fff',
    border: 'none',
    padding: '14px',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 600,
    cursor: 'pointer',
    fontFamily: 'inherit',
  },
  bigStopBtn: {
    width: '100%',
    backgroundColor: '#ef4444',
    color: '#fff',
    border: 'none',
    padding: '14px',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 600,
    cursor: 'pointer',
    fontFamily: 'inherit',
  },
  scheduleList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '16px',
  },
  scheduleItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    padding: '16px',
    backgroundColor: '#1f1f1f',
    borderRadius: '8px',
  },
  scheduleIcon: {
    fontSize: '24px',
  },
  scheduleInfo: {
    display: 'flex',
    flexDirection: 'column' as const,
  },
  scheduleName: {
    fontWeight: 500,
    color: '#e5e5e5',
  },
  scheduleTime: {
    fontSize: '13px',
    color: '#737373',
  },
  scheduleDesc: {
    color: '#737373',
    marginBottom: '20px',
    lineHeight: 1.6,
  },
  manualBtn: {
    width: '100%',
    backgroundColor: '#f59e0b',
    color: '#0f0f0f',
    border: 'none',
    padding: '14px',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 600,
    cursor: 'pointer',
    fontFamily: 'inherit',
  },
  footer: {
    textAlign: 'center' as const,
    padding: '24px',
    color: '#525252',
    fontSize: '13px',
    borderTop: '1px solid #262626',
    marginTop: '40px',
  },
}



