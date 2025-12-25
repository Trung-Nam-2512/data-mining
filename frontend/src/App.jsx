/**
 * Main App Component
 */
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import './styles/App.css'

function App() {
  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <div className="container">
          <Sidebar />
          <HomePage />
        </div>
      </main>
      <Footer />
    </div>
  )
}

export default App
