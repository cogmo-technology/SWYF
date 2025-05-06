import { 
  Shield, 
  Network, 
  FileCode, 
  Eye, 
  Zap, 
  LockKeyhole, 
  CoinsIcon, 
  BarChart3, 
  RefreshCcw, 
  ArrowRightLeft, 
  ChevronRight,
  CreditCard,
  Clock,
  CheckCircle,
  Info,
  ExternalLink,
  Users,
  Activity,
  TrendingUp,
  AlertCircle
} from 'lucide-react';
import Layout from '@/components/Layout';
import { useState, useEffect } from 'react';
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

const getColorClasses = (color: string) => {
  switch (color) {
    case 'blue':
      return {
        bg: 'bg-blue-400/10',
        text: 'text-blue-500'
      };
    case 'purple':
      return {
        bg: 'bg-purple-400/10',
        text: 'text-purple-500'
      };
    case 'green':
      return {
        bg: 'bg-green-400/10',
        text: 'text-green-500'
      };
    default:
      return {
        bg: 'bg-blue-400/10',
        text: 'text-blue-500'
      };
  }
};

const BlockchainFeatures = () => {
  const [activeFeature, setActiveFeature] = useState('security');
  const [networkStats, setNetworkStats] = useState({
    transactions: 0,
    activeNodes: 0,
    blockHeight: 0
  });
  const [isLoading, setIsLoading] = useState(true);
  
  // Simulate real-time network stats
  useEffect(() => {
    const interval = setInterval(() => {
      setNetworkStats(prev => ({
        transactions: prev.transactions + Math.floor(Math.random() * 10),
        activeNodes: Math.floor(Math.random() * 50) + 100,
        blockHeight: prev.blockHeight + 1
      }));
    }, 3000);
    
    return () => clearInterval(interval);
  }, []);

  const features = {
    security: {
      title: 'Enhanced Security',
      icon: Shield,
      color: 'blue',
      description: 'Our blockchain implementation provides industry-leading security for all your transactions and personal data.',
      details: [
        {
          title: 'Immutable Records',
          description: 'Once data is recorded on our blockchain, it cannot be altered, ensuring the integrity of all transactions.',
          icon: LockKeyhole
        },
        {
          title: 'Cryptographic Protection',
          description: 'Advanced encryption secures your personal information and transaction history from unauthorized access.',
          icon: Shield
        },
        {
          title: 'Multi-Signature Authentication',
          description: 'Enhanced security through multiple verification steps for high-value transactions.',
          icon: LockKeyhole
        }
      ]
    },
    decentralization: {
      title: 'Decentralization',
      icon: Network,
      color: 'purple',
      description: 'Our decentralized approach eliminates single points of failure and distributes control.',
      details: [
        {
          title: 'Peer-to-Peer Network',
          description: 'Direct transactions between users without intermediaries, reducing costs and increasing efficiency.',
          icon: ArrowRightLeft
        },
        {
          title: 'Distributed Authority',
          description: 'No single entity controls the network, ensuring fairness and preventing manipulation.',
          icon: Network
        },
        {
          title: 'Community Governance',
          description: 'Token holders can participate in platform decisions and protocol upgrades.',
          icon: Users
        }
      ]
    },
    smartContracts: {
      title: 'Smart Contracts',
      icon: FileCode,
      color: 'green',
      description: 'Self-executing contracts with the terms directly written into code.',
      details: [
        {
          title: 'Automated Execution',
          description: 'Transactions automatically execute when conditions are met, eliminating delays and human error.',
          icon: RefreshCcw
        },
        {
          title: 'Tokenized Rewards',
          description: 'Earn tokens through our smart contract-powered loyalty program that automatically rewards your actions.',
          icon: CoinsIcon
        },
        {
          title: 'Escrow Services',
          description: 'Secure holding of funds until all conditions of a transaction are met.',
          icon: LockKeyhole
        }
      ]
    }
  };

  return (
    <Layout>
      <div className="pt-32 pb-20">
        {/* Background elements with animated gradient */}
        <motion.div 
          className="absolute inset-0 -z-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1 }}
        >
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-400/20 via-blue-500/10 to-background"></div>
          <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10"></div>
        </motion.div>
        
        {/* Introduction with animated text */}
        <section className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-5xl">
          <motion.div 
            className="text-center max-w-3xl mx-auto mb-16"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <motion.span 
              className="px-3 py-1 rounded-full bg-blue-500/10 text-blue-500 text-xs font-medium inline-block mb-4"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Revolutionary Technology
            </motion.span>
            <h1 className="text-4xl md:text-5xl font-display font-bold mb-6">
              Powered by <span className="text-gradient">Blockchain</span>
            </h1>
            <p className="text-lg text-foreground/80 mb-8">
              SWYF integrates cutting-edge blockchain technology to enhance security, transparency, and efficiency in your fashion experience.
            </p>
            <div className="flex items-center justify-center space-x-4">
              <motion.a 
                href="#features" 
                className="px-6 py-3 rounded-full bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-all shadow-lg hover:shadow-primary/20"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Explore Features
              </motion.a>
              <motion.a 
                href="#learn-more" 
                className="px-6 py-3 rounded-full bg-white/10 text-foreground font-medium hover:bg-white/20 transition-all flex items-center"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Learn More
                <ExternalLink size={16} className="ml-2" />
              </motion.a>
            </div>
          </motion.div>
        </section>
        
        {/* Network Stats */}
        <section className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl mb-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <motion.div 
              className="glass-card rounded-xl p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center mr-4">
                    <Activity size={20} className="text-blue-500" />
                  </div>
                  <div>
                    <h4 className="font-medium">Active Nodes</h4>
                    <p className="text-2xl font-bold">{networkStats.activeNodes}</p>
                  </div>
                </div>
                <TrendingUp className="text-green-500" />
              </div>
            </motion.div>
            
            <motion.div 
              className="glass-card rounded-xl p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-purple-500/10 flex items-center justify-center mr-4">
                    <RefreshCcw size={20} className="text-purple-500" />
                  </div>
                  <div>
                    <h4 className="font-medium">Transactions</h4>
                    <p className="text-2xl font-bold">{networkStats.transactions}</p>
                  </div>
                </div>
                <TrendingUp className="text-green-500" />
              </div>
            </motion.div>
            
            <motion.div 
              className="glass-card rounded-xl p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.6 }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-green-500/10 flex items-center justify-center mr-4">
                    <BarChart3 size={20} className="text-green-500" />
                  </div>
                  <div>
                    <h4 className="font-medium">Block Height</h4>
                    <p className="text-2xl font-bold">#{networkStats.blockHeight}</p>
                  </div>
                </div>
                <TrendingUp className="text-green-500" />
              </div>
            </motion.div>
          </div>
        </section>
        
        {/* Main Features with animations */}
        <section id="features" className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            {Object.entries(features).map(([key, feature], index) => {
              const colors = getColorClasses(feature.color);
              return (
                <motion.button
                  key={key}
                  onClick={() => setActiveFeature(key)}
                  className={`glass-card rounded-2xl p-6 transition-all duration-300 hover:shadow-lg ${
                    activeFeature === key ? 'ring-2 ring-primary' : ''
                  }`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className={`w-12 h-12 rounded-full ${colors.bg} flex items-center justify-center mb-4`}>
                    {React.createElement(feature.icon, { size: 24, className: colors.text })}
                  </div>
                  <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                  <p className="text-foreground/70 text-sm">{feature.description}</p>
                </motion.button>
              );
            })}
          </div>

          {/* Feature Details with animations */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeFeature}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="glass-card rounded-2xl p-8 transition-all duration-300"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <div className={`w-14 h-14 rounded-full ${getColorClasses(features[activeFeature].color).bg} flex items-center justify-center mb-6`}>
                    {React.createElement(features[activeFeature].icon, { 
                      size: 28, 
                      className: getColorClasses(features[activeFeature].color).text 
                    })}
                  </div>
                  <h3 className="text-2xl font-bold mb-4">{features[activeFeature].title}</h3>
                  <p className="text-foreground/70 mb-6">{features[activeFeature].description}</p>
                  
                  <div className="space-y-6">
                    {features[activeFeature].details.map((detail, index) => (
                      <motion.div 
                        key={index} 
                        className="flex items-start"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.1 }}
                      >
                        <div className="mt-1">
                          {React.createElement(detail.icon, { 
                            size: 18, 
                            className: `${getColorClasses(features[activeFeature].color).text} mr-3` 
                          })}
                        </div>
                        <div>
                          <h4 className="font-medium">{detail.title}</h4>
                          <p className="text-sm text-foreground/70">{detail.description}</p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
                
                <div className="flex items-center justify-center">
                  <motion.div 
                    className="relative w-full max-w-md"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                  >
                    {/* Animated gradient background */}
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-primary/50 via-accent/50 to-purple-500/50 rounded-lg blur opacity-75 animate-pulse"></div>
                    
                    {/* Main card content */}
                    <div className="relative glass-card backdrop-blur-xl border border-white/10 rounded-lg p-6 shadow-2xl">
                      <div className="flex flex-col space-y-4">
                        {/* Header */}
                        <div className="flex items-center justify-between border-b border-white/10 pb-4">
                          <div className="flex items-center">
                            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center mr-3">
                              {React.createElement(features[activeFeature].icon, { 
                                size: 16, 
                                className: 'text-primary'
                              })}
                            </div>
                            <span className="font-medium text-white/90">Live Demo</span>
                          </div>
                          <motion.div 
                            className="flex items-center gap-2"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.3 }}
                          >
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                            <span className="text-green-500 text-sm font-medium">Active</span>
                          </motion.div>
                        </div>
                        
                        {/* Status Information */}
                        <div className="space-y-4">
                          <motion.div 
                            className="flex items-center justify-between"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.4 }}
                          >
                            <span className="text-sm text-white/70">Transaction Status</span>
                            <span className="text-sm font-medium text-green-500 flex items-center bg-green-500/10 px-2 py-1 rounded-full">
                              <CheckCircle size={14} className="mr-1.5" />
                              Verified
                            </span>
                          </motion.div>
                          
                          <motion.div 
                            className="flex items-center justify-between"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.5 }}
                          >
                            <span className="text-sm text-white/70">Block Height</span>
                            <motion.div 
                              className="flex items-center bg-blue-500/10 px-2 py-1 rounded-full"
                              key={networkStats.blockHeight}
                              initial={{ opacity: 0, scale: 0.9 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{ duration: 0.3 }}
                            >
                              <BarChart3 size={14} className="mr-1.5 text-blue-500" />
                              <span className="text-sm font-medium text-blue-500">#{networkStats.blockHeight}</span>
                            </motion.div>
                          </motion.div>
                          
                          <motion.div 
                            className="flex items-center justify-between"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.6 }}
                          >
                            <span className="text-sm text-white/70">Network</span>
                            <span className="text-sm font-medium flex items-center bg-purple-500/10 px-2 py-1 rounded-full">
                              <Network size={14} className="mr-1.5 text-purple-500" />
                              <span className="text-purple-500">SWYF Mainnet</span>
                            </span>
                          </motion.div>
                        </div>
                        
                        {/* Action Button */}
                        <motion.button 
                          className="w-full mt-2 px-4 py-3 bg-gradient-to-r from-primary/80 to-accent/80 text-white rounded-lg hover:from-primary hover:to-accent transition-all flex items-center justify-center group shadow-xl shadow-primary/20"
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.7 }}
                        >
                          <Info size={16} className="mr-2" />
                          View Transaction Details
                          <ChevronRight size={16} className="ml-1 group-hover:translate-x-1 transition-transform" />
                        </motion.button>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </div>
            </motion.div>
          </AnimatePresence>
        </section>
        
        {/* Learn More Section */}
        <section id="learn-more" className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl py-12">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="px-3 py-1 rounded-full bg-blue-500/10 text-blue-500 text-xs font-medium inline-block mb-4">
              Deep Dive
            </span>
            <h2 className="text-3xl font-display font-bold mb-6">
              Understanding Our Blockchain
            </h2>
            <p className="text-lg text-foreground/70">
              Learn more about how our blockchain technology works and its benefits for the fashion industry.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="glass-card rounded-2xl p-8">
              <h3 className="text-2xl font-bold mb-4">Technical Architecture</h3>
              <p className="text-foreground/70 mb-6">
                Our blockchain implementation uses a hybrid consensus mechanism combining Proof of Stake (PoS) and Proof of Authority (PoA) for optimal performance and security.
              </p>
              <ul className="space-y-4">
                <li className="flex items-start">
                  <CheckCircle size={18} className="text-green-500 mr-3 mt-1" />
                  <div>
                    <h4 className="font-medium">High Performance</h4>
                    <p className="text-sm text-foreground/70">Process thousands of transactions per second</p>
                  </div>
                </li>
                <li className="flex items-start">
                  <CheckCircle size={18} className="text-green-500 mr-3 mt-1" />
                  <div>
                    <h4 className="font-medium">Energy Efficient</h4>
                    <p className="text-sm text-foreground/70">Minimal environmental impact compared to traditional blockchains</p>
                  </div>
                </li>
                <li className="flex items-start">
                  <CheckCircle size={18} className="text-green-500 mr-3 mt-1" />
                  <div>
                    <h4 className="font-medium">Scalable Solution</h4>
                    <p className="text-sm text-foreground/70">Designed to grow with our platform and user base</p>
                  </div>
                </li>
              </ul>
            </div>
            
            <div className="glass-card rounded-2xl p-8">
              <h3 className="text-2xl font-bold mb-4">Industry Impact</h3>
              <p className="text-foreground/70 mb-6">
                Our blockchain technology is revolutionizing the fashion industry by solving key challenges in supply chain transparency and authentication.
              </p>
              <ul className="space-y-4">
                <li className="flex items-start">
                  <CheckCircle size={18} className="text-green-500 mr-3 mt-1" />
                  <div>
                    <h4 className="font-medium">Supply Chain Tracking</h4>
                    <p className="text-sm text-foreground/70">End-to-end visibility of product journey</p>
                  </div>
                </li>
                <li className="flex items-start">
                  <CheckCircle size={18} className="text-green-500 mr-3 mt-1" />
                  <div>
                    <h4 className="font-medium">Authentication</h4>
                    <p className="text-sm text-foreground/70">Verify product authenticity instantly</p>
                  </div>
                </li>
                <li className="flex items-start">
                  <CheckCircle size={18} className="text-green-500 mr-3 mt-1" />
                  <div>
                    <h4 className="font-medium">Sustainability</h4>
                    <p className="text-sm text-foreground/70">Track and verify sustainable practices</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
};

export default BlockchainFeatures; 