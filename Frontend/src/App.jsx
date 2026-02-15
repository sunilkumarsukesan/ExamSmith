import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider, ProtectedRoute } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import About from './pages/About';
import Contact from './pages/Contact';
import SignIn from './pages/SignIn';
import Student from './pages/Student';
import Teacher from './pages/Teacher';
import Admin from './pages/Admin';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
          <Navbar />
          <main style={{ flex: 1 }}>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Home />} />
              <Route path="/about" element={<About />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/signin" element={<SignIn />} />
              
              {/* Protected Routes */}
              <Route 
                path="/student" 
                element={
                  <ProtectedRoute requiredRoles={['ADMIN', 'INSTRUCTOR', 'STUDENT']}>
                    <Student />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/teacher" 
                element={
                  <ProtectedRoute requiredRoles={['ADMIN', 'INSTRUCTOR']}>
                    <Teacher />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/admin" 
                element={
                  <ProtectedRoute requiredRoles={['ADMIN']}>
                    <Admin />
                  </ProtectedRoute>
                } 
              />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
