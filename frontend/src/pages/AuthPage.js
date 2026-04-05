import { useState } from 'react';
import { motion } from 'framer-motion';
import { auth } from '@/lib/firebase';
import { createUserWithEmailAndPassword, signInWithEmailAndPassword } from 'firebase/auth';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import athenaImg from '@/athena2.png';

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        await signInWithEmailAndPassword(auth, email, password);
        toast.success('Welcome back!');
      } else {
        await createUserWithEmailAndPassword(auth, email, password);
        toast.success('Account created successfully!');
      }
      navigate('/dashboard');
    } catch (error) {
      console.log(error.code);
      let message = "Something went wrong. Try again.";
      if (error.code === "auth/user-not-found") {
        setIsLogin(false); //Auto switch to sign up if user not found
        message = "No account found. Switching to Sign Up...";
      } 
      else if (error.code === "auth/wrong-password") {
        message = "Incorrect password. Try again.";
      } 
      else if (error.code === "auth/email-already-in-use") {
        setIsLogin(true); //Auto switch to sign in if email already exists
        message = "Account already exists. Switching to Sign In...";
      } 
      else if (error.code === "auth/invalid-email") {
        message = "Invalid email format.";
      } 
      else if (error.code === "auth/weak-password") {
        message = "Password should be at least 6 characters.";
      }
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
      {/* Left side - Auth form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8" style={{ backgroundColor: '#030712' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-md"
        >
          {/* Logo/Title */}
          <div className="text-center mb-12">
            <motion.h1
              className="text-5xl font-medium mb-3"
              style={{
                fontFamily: "'Cormorant Garamond', serif",
                color: '#D4AF37',
                letterSpacing: '0.02em'
              }}
            >
              ATHENA
            </motion.h1>
            <p className="text-base" style={{ color: '#94A3B8' }}>
              Unbiased AI Reasoning System
            </p>
          </div>

          {/* Auth Form */}
          <div
            className="p-8 border rounded-md"
            style={{
              backgroundColor: '#0B101A',
              borderColor: 'rgba(255, 255, 255, 0.1)'
            }}
          >
            <h2
              className="text-2xl font-normal mb-6"
              style={{
                fontFamily: "'Cormorant Garamond', serif",
                color: '#F8FAFC'
              }}
            >
              {isLogin ? 'Welcome Back' : 'Create Account'}
            </h2>

            <form onSubmit={handleAuth} className="space-y-6">
              <div>
                <Label htmlFor="email" className="text-sm" style={{ color: '#94A3B8' }}>
                  Email
                </Label>
                <Input
                  id="email"
                  data-testid="auth-email-input"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="mt-2 bg-transparent border-b border-t-0 border-x-0 rounded-none px-0 focus:border-[#D4AF37] transition-colors duration-300"
                  style={{
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    color: '#F8FAFC'
                  }}
                  placeholder="Enter your email"
                />
              </div>

              <div>
                <Label htmlFor="password" className="text-sm" style={{ color: '#94A3B8' }}>
                  Password
                </Label>
                <Input
                  id="password"
                  data-testid="auth-password-input"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="mt-2 bg-transparent border-b border-t-0 border-x-0 rounded-none px-0 focus:border-[#D4AF37] transition-colors duration-300"
                  style={{
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    color: '#F8FAFC'
                  }}
                  placeholder="Enter your password"
                />
              </div>

              <Button
                data-testid="auth-submit-button"
                type="submit"
                disabled={loading}
                className="w-full text-sm font-medium tracking-wide transition-all duration-300"
                style={{
                  backgroundColor: '#D4AF37',
                  color: '#030712',
                  border: 'none'
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = '#FBE689';
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = '#D4AF37';
                }}
              >
                {loading ? 'Processing...' : isLogin ? 'Sign In' : 'Create Account'}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <button
                data-testid="auth-toggle-button"
                onClick={() => setIsLogin(!isLogin)}
                className="text-sm transition-colors duration-300"
                style={{ color: '#94A3B8' }}
                onMouseEnter={(e) => {
                  e.target.style.color = '#D4AF37';
                }}
                onMouseLeave={(e) => {
                  e.target.style.color = '#94A3B8';
                }}
              >
                {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
              </button>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Right side - Image */}
      <div
        className="hidden lg:block lg:w-1/2 relative overflow-hidden"
        style={{
          backgroundImage: `url(${athenaImg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        <div
          className="absolute inset-0"
          style={{
            background: 'linear-gradient(135deg, rgba(3, 7, 18, 0.7) 0%, rgba(212, 175, 55, 0.1) 100%)'
          }}
        />
      </div>
    </div>
  );
};

export default AuthPage;
