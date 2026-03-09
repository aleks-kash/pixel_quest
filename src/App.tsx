/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Play, RotateCcw, Trophy, Heart, Coins, Info, Volume2, VolumeX } from 'lucide-react';

// --- Sound Service ---

const SoundService = {
  ctx: null as AudioContext | null,

  init() {
    if (!this.ctx) {
      this.ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
  },

  playTone(freq: number, type: OscillatorType, duration: number, volume: number = 0.1) {
    if (!this.ctx) return;
    if (this.ctx.state === 'suspended') this.ctx.resume();

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = type;
    osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
    
    gain.gain.setValueAtTime(volume, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + duration);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start();
    osc.stop(this.ctx.currentTime + duration);
  },

  playJump() {
    this.playTone(400, 'square', 0.1, 0.05);
    setTimeout(() => this.playTone(600, 'square', 0.1, 0.05), 50);
  },

  playCoin() {
    this.playTone(800, 'sine', 0.1, 0.1);
    setTimeout(() => this.playTone(1200, 'sine', 0.2, 0.1), 50);
  },

  playHurt() {
    this.playTone(150, 'sawtooth', 0.3, 0.1);
  },

  playEnemyDie() {
    this.playTone(200, 'square', 0.1, 0.1);
    this.playTone(100, 'square', 0.2, 0.1);
  },

  playWin() {
    const notes = [523.25, 659.25, 783.99, 1046.50];
    notes.forEach((note, i) => {
      setTimeout(() => this.playTone(note, 'triangle', 0.4, 0.1), i * 150);
    });
  },

  playGameOver() {
    const notes = [440, 349.23, 293.66, 220];
    notes.forEach((note, i) => {
      setTimeout(() => this.playTone(note, 'sawtooth', 0.6, 0.1), i * 200);
    });
  },

  playStart() {
    this.playTone(440, 'sine', 0.1, 0.1);
    setTimeout(() => this.playTone(880, 'sine', 0.2, 0.1), 100);
  },

  playShoot() {
    this.playTone(600, 'sine', 0.05, 0.05);
    this.playTone(300, 'sine', 0.1, 0.05);
  },

  playGingerbreadHurt() {
    this.playTone(300, 'triangle', 0.1, 0.1);
    this.playTone(200, 'triangle', 0.1, 0.1);
  }
};

// --- Types & Constants ---

interface Entity {
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
}

interface Player extends Entity {
  vx: number;
  vy: number;
  isJumping: boolean;
  onGround: boolean;
  health: number;
  score: number;
  direction: 'left' | 'right';
  invulnerableUntil: number;
  dropTimer: number;
}

interface Platform extends Entity {
  type: 'solid' | 'lava' | 'goal' | 'wood';
}

interface NPC extends Entity {
  vx: number;
  type: 'enemy' | 'friendly' | 'gingerbread';
  patrolRange: number;
  startX: number;
  health: number;
  maxHealth: number;
  shootCooldown: number;
  lastShootTime: number;
}

interface Projectile extends Entity {
  vx: number;
  vy: number;
  owner: 'npc' | 'player';
  distance: number;
  maxDistance: number;
}

interface Coin extends Entity {
  collected: boolean;
}

interface HeartItem extends Entity {
  collected: boolean;
}

const GRAVITY = 0.6;
const FRICTION = 0.85;
const JUMP_FORCE = -12;
const SPEED = 0.8;
const MAX_SPEED = 5;
const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 450;

// --- Game Component ---

export default function App() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [gameState, setGameState] = useState<'menu' | 'playing' | 'gameOver' | 'win'>('menu');
  const [score, setScore] = useState(0);
  const [health, setHealth] = useState(3);
  const [level, setLevel] = useState(1);
  const [nextLevel, setNextLevel] = useState(2);
  const [isMuted, setIsMuted] = useState(false);

  // Game state refs (to avoid React re-render overhead in loop)
  const playerRef = useRef<Player & { knockback: number }>({
    x: 50,
    y: 300,
    vx: 0,
    vy: 0,
    width: 32,
    height: 48,
    color: '#3B82F6',
    isJumping: false,
    onGround: false,
    health: 3,
    score: 0,
    direction: 'right',
    invulnerableUntil: 0,
    dropTimer: 0,
    knockback: 0
  });

  const platformsRef = useRef<Platform[]>([
    { x: 0, y: 400, width: 600, height: 50, color: '#1F2937', type: 'solid' }, // Ground 1
    { x: 700, y: 400, width: 600, height: 50, color: '#1F2937', type: 'solid' }, // Ground 2
    { x: 600, y: 320, width: 100, height: 20, color: '#78350F', type: 'wood' }, // Bridge platform
    { x: 250, y: 300, width: 120, height: 20, color: '#78350F', type: 'wood' },
    { x: 450, y: 220, width: 120, height: 20, color: '#78350F', type: 'wood' },
    { x: 800, y: 300, width: 120, height: 20, color: '#78350F', type: 'wood' },
    { x: 1000, y: 220, width: 120, height: 20, color: '#78350F', type: 'wood' },
    { x: 1200, y: 150, width: 100, height: 20, color: '#10B981', type: 'goal' }, // Goal
    { x: 600, y: 420, width: 100, height: 30, color: '#EF4444', type: 'lava' }, // Lava pit
  ]);

  const coinsRef = useRef<Coin[]>([
    { x: 300, y: 260, width: 15, height: 15, color: '#FBBF24', collected: false },
    { x: 500, y: 180, width: 15, height: 15, color: '#FBBF24', collected: false },
    { x: 650, y: 280, width: 15, height: 15, color: '#FBBF24', collected: false },
    { x: 850, y: 260, width: 15, height: 15, color: '#FBBF24', collected: false },
    { x: 1050, y: 180, width: 15, height: 15, color: '#FBBF24', collected: false },
  ]);

  const npcsRef = useRef<NPC[]>([]);
  const projectilesRef = useRef<Projectile[]>([]);
  const heartsRef = useRef<HeartItem[]>([]);

  const keysRef = useRef<{ [key: string]: boolean }>({});
  const cameraRef = useRef({ x: 0 });

  // --- Level Management ---

  const loadLevel = (lvl: number) => {
    if (lvl === 0) {
      // Hub (Safe Zone)
      platformsRef.current = [
        { x: 0, y: 0, width: 30, height: 450, color: '#451a03', type: 'solid' }, // Left Wall
        { x: 770, y: 0, width: 30, height: 450, color: '#451a03', type: 'solid' }, // Right Wall
        { x: 0, y: 400, width: 800, height: 50, color: '#78350f', type: 'solid' }, // Floor
        { x: 0, y: 0, width: 800, height: 50, color: '#451a03', type: 'solid' }, // Ceiling
        { x: 640, y: 260, width: 40, height: 120, color: 'transparent', type: 'goal' }, // Fireplace Portal (Goal)
        { x: 600, y: 380, width: 120, height: 20, color: '#451a03', type: 'solid' }, // Step under portal
      ];
      coinsRef.current = [];
      npcsRef.current = [
        { x: 400, y: 360, width: 32, height: 40, color: '#8B5CF6', vx: 0, type: 'friendly', patrolRange: 0, startX: 400, health: 1, maxHealth: 1, shootCooldown: 0, lastShootTime: 0 },
      ];
      heartsRef.current = [];
    } else if (lvl === 1) {
      platformsRef.current = [
        { x: 0, y: 400, width: 600, height: 50, color: '#1F2937', type: 'solid' },
        { x: 700, y: 400, width: 600, height: 50, color: '#1F2937', type: 'solid' },
        { x: 600, y: 320, width: 100, height: 20, color: '#78350F', type: 'wood' },
        { x: 250, y: 300, width: 120, height: 20, color: '#78350F', type: 'wood' },
        { x: 450, y: 220, width: 120, height: 20, color: '#78350F', type: 'wood' },
        { x: 800, y: 300, width: 120, height: 20, color: '#78350F', type: 'wood' },
        { x: 1000, y: 220, width: 120, height: 20, color: '#78350F', type: 'wood' },
        { x: 1200, y: 150, width: 100, height: 20, color: '#10B981', type: 'goal' },
        { x: 600, y: 420, width: 100, height: 30, color: '#EF4444', type: 'lava' },
      ];
      coinsRef.current = [
        { x: 300, y: 260, width: 15, height: 15, color: '#FBBF24', collected: false },
        { x: 500, y: 180, width: 15, height: 15, color: '#FBBF24', collected: false },
        { x: 650, y: 280, width: 15, height: 15, color: '#FBBF24', collected: false },
        { x: 850, y: 260, width: 15, height: 15, color: '#FBBF24', collected: false },
        { x: 1050, y: 180, width: 15, height: 15, color: '#FBBF24', collected: false },
      ];
      npcsRef.current = [
        { x: 400, y: 368, width: 32, height: 32, color: '#DC2626', vx: 2, type: 'enemy', patrolRange: 150, startX: 400, health: 1, maxHealth: 1, shootCooldown: 0, lastShootTime: 0 },
        { x: 900, y: 368, width: 32, height: 32, color: '#DC2626', vx: -2, type: 'enemy', patrolRange: 150, startX: 900, health: 1, maxHealth: 1, shootCooldown: 0, lastShootTime: 0 },
        { x: 100, y: 368, width: 32, height: 40, color: '#8B5CF6', vx: 0, type: 'friendly', patrolRange: 0, startX: 100, health: 1, maxHealth: 1, shootCooldown: 0, lastShootTime: 0 },
      ];
      heartsRef.current = [
        { x: 1100, y: 110, width: 20, height: 20, color: '#EF4444', collected: false },
      ];
    } else if (lvl === 2) {
      platformsRef.current = [
        { x: 0, y: 400, width: 400, height: 50, color: '#1F2937', type: 'solid' },
        { x: 500, y: 400, width: 400, height: 50, color: '#1F2937', type: 'solid' },
        { x: 1000, y: 400, width: 400, height: 50, color: '#1F2937', type: 'solid' },
        { x: 400, y: 320, width: 100, height: 20, color: '#78350F', type: 'wood' },
        { x: 900, y: 320, width: 100, height: 20, color: '#78350F', type: 'wood' },
        { x: 200, y: 250, width: 150, height: 20, color: '#78350F', type: 'wood' },
        { x: 600, y: 200, width: 150, height: 20, color: '#78350F', type: 'wood' },
        { x: 950, y: 250, width: 150, height: 20, color: '#78350F', type: 'wood' },
        { x: 1250, y: 200, width: 100, height: 20, color: '#78350F', type: 'wood' }, // Added intermediate platform
        { x: 1450, y: 150, width: 100, height: 20, color: '#10B981', type: 'goal' },
        { x: 400, y: 420, width: 100, height: 30, color: '#EF4444', type: 'lava' },
        { x: 900, y: 420, width: 100, height: 30, color: '#EF4444', type: 'lava' },
      ];
      coinsRef.current = [
        { x: 250, y: 210, width: 15, height: 15, color: '#FBBF24', collected: false },
        { x: 650, y: 160, width: 15, height: 15, color: '#FBBF24', collected: false },
        { x: 1150, y: 210, width: 15, height: 15, color: '#FBBF24', collected: false },
      ];
      npcsRef.current = [
        { x: 300, y: 368, width: 32, height: 32, color: '#8B4513', vx: 1, type: 'gingerbread', patrolRange: 100, startX: 300, health: 2, maxHealth: 2, shootCooldown: 2000, lastShootTime: 0 },
        { x: 700, y: 368, width: 32, height: 32, color: '#8B4513', vx: -1, type: 'gingerbread', patrolRange: 100, startX: 700, health: 2, maxHealth: 2, shootCooldown: 2500, lastShootTime: 0 },
        { x: 1200, y: 368, width: 32, height: 32, color: '#8B4513', vx: 1, type: 'gingerbread', patrolRange: 100, startX: 1200, health: 2, maxHealth: 2, shootCooldown: 3000, lastShootTime: 0 },
        { x: 950, y: 218, width: 32, height: 32, color: '#DC2626', vx: 1.5, type: 'enemy', patrolRange: 60, startX: 950, health: 1, maxHealth: 1, shootCooldown: 0, lastShootTime: 0 },
      ];
      heartsRef.current = [
        { x: 1300, y: 110, width: 20, height: 20, color: '#EF4444', collected: false },
      ];
    }
    projectilesRef.current = [];
  };

  // --- Input Handling ---

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      keysRef.current[e.code] = true;
    };
    const handleKeyUp = (e: KeyboardEvent) => {
      keysRef.current[e.code] = false;
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  // --- Game Loop ---

  useEffect(() => {
    if (gameState !== 'playing') return;

    let animationFrameId: number;

      const update = () => {
        const player = playerRef.current;

        // 1. Movement
        if (player.knockback > 0) {
          player.knockback--;
        } else {
          if (keysRef.current['ArrowLeft'] || keysRef.current['KeyA']) {
            player.vx -= SPEED;
            player.direction = 'left';
          }
          if (keysRef.current['ArrowRight'] || keysRef.current['KeyD']) {
            player.vx += SPEED;
            player.direction = 'right';
          }
        }

        if ((keysRef.current['Space'] || keysRef.current['ArrowUp'] || keysRef.current['KeyW']) && player.onGround) {
        player.vy = JUMP_FORCE;
        player.onGround = false;
        player.isJumping = true;
        if (!isMuted) SoundService.playJump();
      }

      if ((keysRef.current['ArrowDown'] || keysRef.current['KeyS']) && player.onGround) {
        // Only allow dropping if on a wood platform
        const isOnWood = platformsRef.current.some(p => 
          p.type === 'wood' &&
          player.x < p.x + p.width &&
          player.x + player.width > p.x &&
          Math.abs(player.y + player.height - p.y) <= 2
        );

        if (isOnWood) {
          player.dropTimer = 15;
          player.onGround = false;
          player.y += 5; // Small push to start falling
        }
      }

      // 2. Physics
      player.vx *= FRICTION;
      player.vy += GRAVITY;
      player.x += player.vx;
      player.y += player.vy;

      // Hub boundaries (fixed screen)
      if (level === 0) {
        if (player.x < 30) {
          player.x = 30;
          player.vx = 0;
        }
        if (player.x + player.width > 770) {
          player.x = 770 - player.width;
          player.vx = 0;
        }
      }

      // Clamp speed
      if (Math.abs(player.vx) > MAX_SPEED) player.vx = Math.sign(player.vx) * MAX_SPEED;

      // 3. Collision Detection (Platforms)
      player.onGround = false;
      if (player.dropTimer > 0) player.dropTimer--;

      platformsRef.current.forEach(platform => {
        // Simple AABB overlap check
        const isOverlapping = 
          player.x < platform.x + platform.width &&
          player.x + player.width > platform.x &&
          player.y < platform.y + platform.height &&
          player.y + player.height > platform.y;

        if (isOverlapping) {
          // Goal triggers on overlap (allows entering from front)
          if (platform.type === 'goal') {
            if (!isMuted) SoundService.playWin();
            
            if (level === 0) {
              // Leaving Hub to Next Level
              setLevel(nextLevel);
              loadLevel(nextLevel);
              player.x = 50;
              player.y = 300;
              player.vx = 0;
              player.vy = 0;
            } else if (level === 2) {
              // Finished last level
              setGameState('win');
            } else {
              // Finished level, go to Hub
              setNextLevel(level + 1);
              setLevel(0);
              loadLevel(0);
              player.x = 80; // Start on the left in the hub (from green portal)
              player.y = 350;
              player.vx = 0;
              player.vy = 0;
            }
            return;
          }

          if (platform.type === 'lava') {
            handleDeath();
            return;
          }
        }

        // Skip platforms if dropping (only wood platforms allow dropping)
        if (platform.type === 'wood' && player.dropTimer > 0) return;

        // One-way platform logic for wood: only collide if falling and above
        if (platform.type === 'wood' && player.vy < 0) return;

        if (isOverlapping) {
          // Resolve collision (Top down)
          if (player.vy > 0 && player.y + player.height - player.vy <= platform.y + platform.height) {
             // Check if it's a solid/wood platform
             if (platform.type === 'solid' || platform.type === 'wood') {
                // Check if player is falling onto the platform
                if (player.y + player.height - player.vy <= platform.y) {
                  player.y = platform.y - player.height;
                  player.vy = 0;
                  player.onGround = true;
                  player.isJumping = false;
                }
             }
          }
        }
      });

      // 4. Collision Detection (Coins)
      coinsRef.current.forEach(coin => {
        if (!coin.collected &&
          player.x < coin.x + coin.width &&
          player.x + player.width > coin.x &&
          player.y < coin.y + coin.height &&
          player.y + player.height > coin.y
        ) {
          coin.collected = true;
          setScore(prev => prev + 10);
          if (!isMuted) SoundService.playCoin();
        }
      });

      // 4.5 Collision Detection (Hearts)
      heartsRef.current.forEach(heart => {
        if (!heart.collected &&
          player.x < heart.x + heart.width &&
          player.x + player.width > heart.x &&
          player.y < heart.y + heart.height &&
          player.y + player.height > heart.y
        ) {
          heart.collected = true;
          player.health += 1;
          setHealth(player.health);
          if (!isMuted) SoundService.playCoin(); // Reuse coin sound or add new
        }
      });

      // 5. NPCs Update & Collision
      const now = Date.now();
      npcsRef.current.forEach(npc => {
        if (npc.health <= 0) return;

        if (npc.type === 'enemy' || npc.type === 'gingerbread') {
          npc.x += npc.vx;
          if (Math.abs(npc.x - npc.startX) > npc.patrolRange) {
            npc.vx *= -1;
          }

          // Gingerbread shooting
          if (npc.type === 'gingerbread' && now - npc.lastShootTime > npc.shootCooldown) {
            const dir = player.x < npc.x ? -1 : 1;
            projectilesRef.current.push({
              x: npc.x + (dir === 1 ? npc.width : -10),
              y: npc.y + npc.height / 2 - 5,
              width: 10,
              height: 10,
              color: '#FFFFFF',
              vx: dir * 4,
              vy: 0,
              owner: 'npc',
              distance: 0,
              maxDistance: 350
            });
            npc.lastShootTime = now;
            if (!isMuted) SoundService.playShoot();
          }

          // Collision with player
          if (
            player.x < npc.x + npc.width &&
            player.x + player.width > npc.x &&
            player.y < npc.y + npc.height &&
            player.y + player.height > npc.y
          ) {
            // If jumping on top
            const isStomp = player.vy > 0 && (player.y + player.height - player.vy <= npc.y + 15);
            if (isStomp) {
              npc.health -= 1;
              player.vy = -8; // Bounce
              if (npc.health <= 0) {
                npc.y = -1000; // Move out of screen
                setScore(prev => prev + 50);
                if (!isMuted) SoundService.playEnemyDie();
              } else {
                if (!isMuted) SoundService.playGingerbreadHurt();
              }
            } else {
              handleDamage();
            }
          }
        }
      });

      // 5.5 Projectiles Update
      projectilesRef.current = projectilesRef.current.filter((p) => {
        p.x += p.vx;
        p.y += p.vy;
        p.distance += Math.sqrt(p.vx * p.vx + p.vy * p.vy);

        // Collision with player
        if (
          p.owner === 'npc' &&
          p.x < player.x + player.width &&
          p.x + p.width > player.x &&
          p.y < player.y + player.height &&
          p.y + p.height > player.y
        ) {
          if (now > player.invulnerableUntil) {
            handleDamage();
            // Knockback
            player.vx = p.vx * 1.5;
            player.vy = -4;
            player.knockback = 15;
          }
          return false;
        }

        // Remove if out of bounds or distance exceeded
        const isOutOfBounds = p.x < cameraRef.current.x - 100 || p.x > cameraRef.current.x + CANVAS_WIDTH + 100;
        const isDistanceExceeded = p.distance > p.maxDistance;
        
        return !isOutOfBounds && !isDistanceExceeded;
      });

      // 6. Camera Follow
      if (level === 0) {
        cameraRef.current.x = 0;
      } else {
        cameraRef.current.x = player.x - CANVAS_WIDTH / 2 + player.width / 2;
        if (cameraRef.current.x < 0) cameraRef.current.x = 0;
      }

      // 7. Bounds check
      if (player.y > CANVAS_HEIGHT + 100) {
        handleDeath();
      }

      draw();
      animationFrameId = requestAnimationFrame(update);
    };

    const drawLevelBackground = (ctx: CanvasRenderingContext2D, lvl: number, camX: number) => {
      if (lvl === 1) {
        ctx.fillStyle = '#E0F2FE'; // Sky Blue
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

        // Distant Hills (Parallax)
        ctx.fillStyle = '#93C5FD'; // Lighter blue-gray
        for (let i = 0; i < 3; i++) {
          const x = ((i * 500 - camX * 0.1) % (CANVAS_WIDTH + 500)) - 250;
          ctx.beginPath();
          ctx.moveTo(x, CANVAS_HEIGHT);
          ctx.lineTo(x + 250, CANVAS_HEIGHT - 150);
          ctx.lineTo(x + 500, CANVAS_HEIGHT);
          ctx.fill();
        }

        // Closer Hills
        ctx.fillStyle = '#60A5FA';
        for (let i = 0; i < 4; i++) {
          const x = ((i * 400 - camX * 0.3) % (CANVAS_WIDTH + 400)) - 200;
          ctx.beginPath();
          ctx.moveTo(x, CANVAS_HEIGHT);
          ctx.lineTo(x + 200, CANVAS_HEIGHT - 80);
          ctx.lineTo(x + 400, CANVAS_HEIGHT);
          ctx.fill();
        }

        // Very Close Bushes (Parallax)
        ctx.fillStyle = '#34D399'; // Emerald 400
        for (let i = 0; i < 6; i++) {
          const x = ((i * 350 - camX * 0.7) % (CANVAS_WIDTH + 350)) - 175;
          ctx.beginPath();
          ctx.ellipse(x, CANVAS_HEIGHT - 5, 60, 30, 0, 0, Math.PI * 2);
          ctx.fill();
          // Add some detail to bushes
          ctx.fillStyle = '#059669';
          ctx.beginPath(); ctx.arc(x - 20, CANVAS_HEIGHT - 15, 10, 0, Math.PI * 2); ctx.fill();
          ctx.beginPath(); ctx.arc(x + 15, CANVAS_HEIGHT - 20, 12, 0, Math.PI * 2); ctx.fill();
          ctx.fillStyle = '#34D399';
        }
        
        // Clouds
        ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
        for (let i = 0; i < 5; i++) {
          const x = ((i * 300 - camX * 0.2) % (CANVAS_WIDTH + 400)) - 200;
          const y = 50 + i * 30;
          ctx.beginPath();
          ctx.arc(x, y, 30, 0, Math.PI * 2);
          ctx.arc(x + 25, y - 5, 25, 0, Math.PI * 2);
          ctx.arc(x - 20, y + 5, 20, 0, Math.PI * 2);
          ctx.fill();
        }
      } else if (lvl === 2) {
        // Night Sky
        ctx.fillStyle = '#1E1B4B'; // Dark Indigo
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

        // Distant Mountains (Night)
        ctx.fillStyle = '#312E81';
        for (let i = 0; i < 3; i++) {
          const x = ((i * 600 - camX * 0.1) % (CANVAS_WIDTH + 600)) - 300;
          ctx.beginPath();
          ctx.moveTo(x, CANVAS_HEIGHT);
          ctx.lineTo(x + 300, CANVAS_HEIGHT - 200);
          ctx.lineTo(x + 600, CANVAS_HEIGHT);
          ctx.fill();
        }

        // Closer Dark Forest Silhouette
        ctx.fillStyle = '#111827';
        for (let i = 0; i < 8; i++) {
          const x = ((i * 200 - camX * 0.6) % (CANVAS_WIDTH + 200)) - 100;
          ctx.beginPath();
          ctx.moveTo(x, CANVAS_HEIGHT);
          ctx.lineTo(x + 50, CANVAS_HEIGHT - 120);
          ctx.lineTo(x + 100, CANVAS_HEIGHT);
          ctx.fill();
        }
        
        // Stars
        ctx.fillStyle = 'white';
        for (let i = 0; i < 50; i++) {
          const x = (i * 12345) % CANVAS_WIDTH;
          const y = (i * 54321) % (CANVAS_HEIGHT - 100);
          const size = (i % 2) + 1;
          ctx.globalAlpha = 0.5 + Math.sin(Date.now() / 1000 + i) * 0.5;
          ctx.fillRect(x, y, size, size);
        }
        ctx.globalAlpha = 1.0;
        
        // Moon
        ctx.fillStyle = '#FDE68A';
        ctx.beginPath();
        ctx.arc(CANVAS_WIDTH - 80, 60, 30, 0, Math.PI * 2);
        ctx.fill();
        // Moon Crater
        ctx.fillStyle = '#F59E0B';
        ctx.globalAlpha = 0.2;
        ctx.beginPath();
        ctx.arc(CANVAS_WIDTH - 90, 50, 8, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1.0;
      } else {
        // Default Sky
        ctx.fillStyle = '#E0F2FE';
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
      }
    };

    const draw = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const camX = cameraRef.current.x;

      // Clear
      ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

      // Background
      if (level === 0) {
        // Hub Background (Inside a cozy house)
        ctx.fillStyle = '#78350f'; // Brown walls
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        
        // Wallpaper pattern
        ctx.strokeStyle = '#451a03';
        ctx.lineWidth = 1;
        for (let i = 0; i < CANVAS_WIDTH; i += 40) {
          ctx.beginPath();
          ctx.moveTo(i, 0);
          ctx.lineTo(i, CANVAS_HEIGHT);
          ctx.stroke();
        }

        // Window
        const winX = 325;
        const winY = 150;
        const winW = 150;
        const winH = 150;

        // Draw what's outside the window (Next Level Background)
        ctx.save();
        ctx.beginPath();
        ctx.rect(winX, winY, winW, winH);
        ctx.clip();
        
        // Offset the background slightly to make it look like it's outside
        ctx.translate(winX - 100, winY - 50);
        ctx.scale(0.8, 0.8); // Scale down a bit to show more
        drawLevelBackground(ctx, nextLevel, 0);
        ctx.restore();

        // Window Frame
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 6;
        ctx.strokeRect(winX, winY, winW, winH);
        ctx.beginPath();
        ctx.moveTo(winX + winW / 2, winY); ctx.lineTo(winX + winW / 2, winY + winH);
        ctx.moveTo(winX, winY + winH / 2); ctx.lineTo(winX + winW, winY + winH / 2);
        ctx.stroke();

        // Fireplace (Portal)
        // Removed gray background as per request
        
        // Portal inside fireplace (Vertical)
        const portalX2 = 640;
        const portalY2 = 260 + Math.sin(Date.now() / 400) * 10;
        ctx.fillStyle = '#F97316';
        ctx.beginPath();
        ctx.arc(portalX2 + 20, portalY2 + 20, 22, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(portalX2 + 25, portalY2 + 50, 18, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(portalX2 + 20, portalY2 + 80, 20, 0, Math.PI * 2);
        ctx.fill();
        
        // Inner glow for portal
        ctx.fillStyle = '#FB923C';
        ctx.beginPath();
        ctx.arc(portalX2 + 20, portalY2 + 20, 10, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(portalX2 + 25, portalY2 + 50, 8, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(portalX2 + 20, portalY2 + 80, 9, 0, Math.PI * 2);
        ctx.fill();

        // Rug
        ctx.fillStyle = '#991b1b'; // Red rug
        ctx.fillRect(200, 380, 400, 20);
        ctx.fillStyle = '#7f1d1d';
        for (let i = 200; i < 600; i += 20) {
          ctx.fillRect(i, 380, 10, 20);
        }

        // Picture on the wall
        ctx.fillStyle = '#451a03'; // Frame
        ctx.fillRect(150, 120, 80, 60);
        ctx.fillStyle = '#fef3c7'; // Canvas
        ctx.fillRect(155, 125, 70, 50);
        ctx.fillStyle = '#34d399'; // Simple landscape in picture
        ctx.beginPath();
        ctx.moveTo(160, 170); ctx.lineTo(190, 140); ctx.lineTo(220, 170);
        ctx.fill();

        // Portals in Hub
        // Left Portal (Green Door) - Where player spawns
        const portalX1 = 60;
        const portalY1 = 320;
        ctx.fillStyle = '#10B981';
        ctx.fillRect(portalX1, portalY1, 80, 80);
        ctx.strokeStyle = '#059669';
        ctx.lineWidth = 4;
        ctx.strokeRect(portalX1, portalY1, 80, 80);
        
        // Door handle
        ctx.fillStyle = '#FBBF24';
        ctx.beginPath();
        ctx.arc(portalX1 + 65, portalY1 + 40, 4, 0, Math.PI * 2);
        ctx.fill();
      } else {
        drawLevelBackground(ctx, level, camX);
      }

      // Draw Platforms
      platformsRef.current.forEach(p => {
        if (p.type === 'lava') {
          const time = Date.now() / 1000;
          ctx.fillStyle = '#EF4444';
          ctx.fillRect(p.x - camX, p.y, p.width, p.height);
          
          // Bubbling effect
          ctx.fillStyle = '#F87171';
          for (let i = 0; i < 3; i++) {
            const bx = p.x - camX + (p.width * (0.2 + i * 0.3) + Math.sin(time * 2 + i) * 10);
            const by = p.y + 5 + Math.cos(time * 3 + i) * 3;
            ctx.beginPath();
            ctx.arc(bx, by, 3 + Math.sin(time * 4 + i) * 2, 0, Math.PI * 2);
            ctx.fill();
          }
          
          // Steam effect
          ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
          for (let i = 0; i < 2; i++) {
            const sx = p.x - camX + (p.width * (0.3 + i * 0.4) + Math.sin(time + i) * 15);
            const sy = p.y - 10 - ((time * 40 + i * 30) % 50);
            const size = 5 + Math.sin(time * 2 + i) * 3;
            ctx.beginPath();
            ctx.arc(sx, sy, size, 0, Math.PI * 2);
            ctx.fill();
          }
        } else {
          ctx.fillStyle = p.color;
          ctx.fillRect(p.x - camX, p.y, p.width, p.height);
        }
        
        if (p.type === 'wood') {
          // Wooden texture
          ctx.strokeStyle = '#451a03';
          ctx.lineWidth = 1;
          for (let i = 4; i < p.height; i += 6) {
            ctx.beginPath();
            ctx.moveTo(p.x - camX, p.y + i);
            ctx.lineTo(p.x - camX + p.width, p.y + i);
            ctx.stroke();
          }
          // Grain
          ctx.fillStyle = '#92400e';
          for (let i = 0; i < p.width; i += 20) {
            ctx.fillRect(p.x - camX + i + Math.random() * 5, p.y + 2, 2, p.height - 4);
          }
        }
      });

      // Draw Coins
      coinsRef.current.forEach(c => {
        if (!c.collected) {
          ctx.fillStyle = c.color;
          ctx.beginPath();
          ctx.arc(c.x - camX + c.width / 2, c.y + c.height / 2, c.width / 2, 0, Math.PI * 2);
          ctx.fill();
          // Shine
          ctx.fillStyle = 'white';
          ctx.beginPath();
          ctx.arc(c.x - camX + c.width / 2 - 2, c.y + c.height / 2 - 2, 2, 0, Math.PI * 2);
          ctx.fill();
        }
      });

      // Draw Hearts
      heartsRef.current.forEach(h => {
        if (!h.collected) {
          ctx.fillStyle = h.color;
          const x = h.x - camX;
          const y = h.y;
          const w = h.width;
          const h_ = h.height;
          
          ctx.beginPath();
          ctx.moveTo(x + w / 2, y + h_ / 4);
          ctx.bezierCurveTo(x + w / 2, y, x, y, x, y + h_ / 4);
          ctx.bezierCurveTo(x, y + h_ / 2, x + w / 2, y + h_ * 0.75, x + w / 2, y + h_);
          ctx.bezierCurveTo(x + w / 2, y + h_ * 0.75, x + w, y + h_ / 2, x + w, y + h_ / 4);
          ctx.bezierCurveTo(x + w, y, x + w / 2, y, x + w / 2, y + h_ / 4);
          ctx.fill();
        }
      });

      // Draw NPCs
      npcsRef.current.forEach(n => {
        if (n.health <= 0) return;
        ctx.fillStyle = n.color;
        
        if (n.type === 'gingerbread') {
          // Draw gingerbread man shape with animation
          const x = n.x - camX;
          const y = n.y;
          const w = n.width;
          const h = n.height;

          // Animation: wobble and slight squash/stretch
          const time = Date.now() / 200;
          const wobble = Math.sin(time) * 8; // Increased wobble
          const scaleY = 1 + Math.sin(time * 2.5) * 0.08; // More squash
          const jumpY = Math.abs(Math.sin(time * 2)) * -5; // Small hop
          
          ctx.save();
          ctx.translate(x + w / 2, y + h + jumpY);
          ctx.scale(1, scaleY);
          ctx.rotate(wobble * Math.PI / 180);
          ctx.translate(-(x + w / 2), -(y + h));

          ctx.fillStyle = n.color;
          // Head
          ctx.beginPath();
          ctx.arc(x + w / 2, y + h / 4, w / 2.5, 0, Math.PI * 2);
          ctx.fill();
          // Body
          ctx.beginPath();
          ctx.ellipse(x + w / 2, y + h / 2 + 5, w / 2.5, h / 2.5, 0, 0, Math.PI * 2);
          ctx.fill();
          // Arms (curved)
          ctx.lineWidth = 8;
          ctx.lineCap = 'round';
          ctx.strokeStyle = n.color;
          ctx.beginPath();
          ctx.moveTo(x + 5, y + h / 2);
          ctx.lineTo(x - 10, y + h / 2 - 5);
          ctx.stroke();
          ctx.beginPath();
          ctx.moveTo(x + w - 5, y + h / 2);
          ctx.lineTo(x + w + 10, y + h / 2 - 5);
          ctx.stroke();
          
          // Legs
          ctx.fillRect(x + 2, y + h - 10, 10, 12);
          ctx.fillRect(x + w - 12, y + h - 10, 10, 12);

          // Icing/Decorations
          ctx.strokeStyle = 'white';
          ctx.lineWidth = 2;
          // Smile
          ctx.beginPath();
          ctx.arc(x + w / 2, y + h / 4 + 2, 5, 0.2, Math.PI - 0.2);
          ctx.stroke();
          
          // Squiggly icing on arms and legs
          ctx.beginPath();
          for(let i=0; i<10; i++) {
            ctx.lineTo(x - 5 + i, y + h/2 - 5 + Math.sin(i)*2);
          }
          ctx.stroke();

          // Buttons
          ctx.fillStyle = '#EF4444';
          ctx.beginPath(); ctx.arc(x + w / 2, y + h / 2, 4, 0, Math.PI * 2); ctx.fill();
          ctx.fillStyle = '#10B981';
          ctx.beginPath(); ctx.arc(x + w / 2, y + h / 2 + 12, 4, 0, Math.PI * 2); ctx.fill();

          // Eyes
          const blink = Math.sin(Date.now() / 500) > 0.9 ? 0.1 : 1;
          ctx.fillStyle = 'white';
          ctx.beginPath(); ctx.arc(x + w / 2 - 6, y + h / 4 - 2, 4, 0, Math.PI * 2); ctx.fill();
          ctx.beginPath(); ctx.arc(x + w / 2 + 6, y + h / 4 - 2, 4, 0, Math.PI * 2); ctx.fill();
          ctx.fillStyle = 'black';
          ctx.save();
          ctx.translate(x + w / 2 - 6, y + h / 4 - 2);
          ctx.scale(1, blink);
          ctx.beginPath(); ctx.arc(0, 0, 2, 0, Math.PI * 2); ctx.fill();
          ctx.restore();
          ctx.save();
          ctx.translate(x + w / 2 + 6, y + h / 4 - 2);
          ctx.scale(1, blink);
          ctx.beginPath(); ctx.arc(0, 0, 2, 0, Math.PI * 2); ctx.fill();
          ctx.restore();
          
          ctx.restore();
        } else if (n.type === 'friendly') {
          // Draw a cozy NPC in the hub
          const x = n.x - camX;
          const y = n.y;
          ctx.fillStyle = '#FCD34D'; // Yellow
          ctx.fillRect(x, y, n.width, n.height);
          // Eyes follow player
          const p = playerRef.current;
          const dx = p.x - n.x;
          const dy = p.y - n.y;
          const dist = Math.max(1, Math.sqrt(dx * dx + dy * dy));
          const lookX = (dx / dist) * 2.5;
          const lookY = (dy / dist) * 2.5;

          ctx.fillStyle = 'white';
          ctx.fillRect(x + 5, y + 10, 6, 6);
          ctx.fillRect(x + n.width - 11, y + 10, 6, 6);
          ctx.fillStyle = 'black';
          ctx.fillRect(x + 7 + lookX, y + 12 + lookY, 2, 2);
          ctx.fillRect(x + n.width - 9 + lookX, y + 12 + lookY, 2, 2);
          // Little hat
          ctx.fillStyle = '#EF4444';
          ctx.beginPath();
          ctx.moveTo(x, y);
          ctx.lineTo(x + n.width / 2, y - 15);
          ctx.lineTo(x + n.width, y);
          ctx.fill();
        } else {
          ctx.fillRect(n.x - camX, n.y, n.width, n.height);
          // Eyes for enemy
          if (n.type === 'enemy') {
            ctx.fillStyle = 'white';
            ctx.fillRect(n.x - camX + 5, n.y + 5, 5, 5);
            ctx.fillRect(n.x - camX + n.width - 10, n.y + 5, 5, 5);
          }
        }

        // Health bar for gingerbread
        if (n.type === 'gingerbread') {
          ctx.fillStyle = '#333';
          ctx.fillRect(n.x - camX, n.y - 10, n.width, 4);
          ctx.fillStyle = '#EF4444';
          ctx.fillRect(n.x - camX, n.y - 10, (n.health / n.maxHealth) * n.width, 4);
        }
      });

      // Draw Projectiles
      projectilesRef.current.forEach(p => {
        if (p.owner === 'npc') {
          // Faveroli cookie
          const x = p.x - camX;
          const y = p.y;
          const r = p.width / 2;
          
          ctx.fillStyle = '#D97706'; // Cookie brown
          ctx.beginPath();
          ctx.arc(x + r, y + r, r, 0, Math.PI * 2);
          ctx.fill();
          
          // Sprinkles/Dots
          ctx.fillStyle = 'white';
          ctx.beginPath(); ctx.arc(x + r - 2, y + r - 2, 1.5, 0, Math.PI * 2); ctx.fill();
          ctx.fillStyle = '#F472B6'; // Pink
          ctx.beginPath(); ctx.arc(x + r + 2, y + r + 1, 1.5, 0, Math.PI * 2); ctx.fill();
          ctx.fillStyle = '#60A5FA'; // Blue
          ctx.beginPath(); ctx.arc(x + r, y + r + 3, 1.5, 0, Math.PI * 2); ctx.fill();
        } else {
          ctx.fillStyle = p.color;
          ctx.beginPath();
          ctx.arc(p.x - camX + p.width / 2, p.y + p.height / 2, p.width / 2, 0, Math.PI * 2);
          ctx.fill();
        }
      });

      // Draw Player
      const player = playerRef.current;
      const now = Date.now();
      const isInvulnerable = now < player.invulnerableUntil;
      const isVisible = !isInvulnerable || Math.floor(now / 150) % 2 === 0;

      if (isVisible) {
        ctx.fillStyle = player.color;
        ctx.fillRect(player.x - camX, player.y, player.width, player.height);
        
        // Player Eyes
        ctx.fillStyle = 'white';
        const eyeOffset = player.direction === 'right' ? 18 : 5;
        ctx.fillRect(player.x - camX + eyeOffset, player.y + 10, 8, 8);
        ctx.fillStyle = 'black';
        const pupilOffset = player.direction === 'right' ? eyeOffset + 4 : eyeOffset + 1;
        ctx.fillRect(player.x - camX + pupilOffset, player.y + 12, 3, 3);
      }
    };

    const handleDamage = () => {
      const player = playerRef.current;
      const now = Date.now();
      if (now < player.invulnerableUntil) return;

      player.health -= 1;
      player.invulnerableUntil = now + 1500;
      setHealth(player.health);
      if (!isMuted) SoundService.playHurt();
      
      // Knockback
      player.vx = player.direction === 'right' ? -10 : 10;
      player.vy = -5;

      if (player.health <= 0) {
        setGameState('gameOver');
        if (!isMuted) SoundService.playGameOver();
      }
    };

    const handleDeath = () => {
      setGameState('gameOver');
      if (!isMuted) SoundService.playGameOver();
    };

    animationFrameId = requestAnimationFrame(update);
    return () => cancelAnimationFrame(animationFrameId);
  }, [gameState, level, isMuted]);

  const startGame = () => {
    SoundService.init();
    if (!isMuted) SoundService.playStart();
    // Reset state
    setLevel(1);
    setNextLevel(2);
    loadLevel(1);
    playerRef.current = {
      x: 50,
      y: 300,
      vx: 0,
      vy: 0,
      width: 32,
      height: 48,
      color: '#3B82F6',
      isJumping: false,
      onGround: false,
      health: 3,
      score: 0,
      direction: 'right',
      invulnerableUntil: 0,
      dropTimer: 0
    };
    cameraRef.current = { x: 0 };
    coinsRef.current.forEach(c => c.collected = false);
    npcsRef.current.forEach(n => {
      if (n.type === 'enemy') {
        n.x = n.startX;
        n.y = 368;
      }
    });
    setScore(0);
    setHealth(3);
    setGameState('playing');
  };

  const continueLevel = () => {
    SoundService.init();
    if (!isMuted) SoundService.playStart();
    // Reset state but keep level and score
    loadLevel(level);
    playerRef.current = {
      x: 50,
      y: 300,
      vx: 0,
      vy: 0,
      width: 32,
      height: 48,
      color: '#3B82F6',
      isJumping: false,
      onGround: false,
      health: 3,
      score: score,
      direction: 'right',
      invulnerableUntil: 0,
      dropTimer: 0
    };
    cameraRef.current = { x: 0 };
    setHealth(3);
    setGameState('playing');
  };

  return (
    <div className="min-h-screen bg-[#F5F5F4] text-[#1C1917] font-sans flex flex-col items-center justify-center p-4">
      {/* Header / HUD */}
      <div className="w-full max-w-[800px] flex justify-between items-center mb-4 bg-white p-4 rounded-2xl shadow-sm border border-black/5">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <Heart className="w-5 h-5 text-red-500 fill-red-500" />
            <span className="font-bold text-xl">{health}</span>
          </div>
          <div className="flex items-center gap-2">
            <Coins className="w-5 h-5 text-yellow-500" />
            <span className="font-bold text-xl">{score}</span>
          </div>
        </div>
        <div className="flex items-center gap-2 bg-stone-100 px-4 py-1 rounded-full">
          <span className="text-sm font-medium uppercase tracking-wider text-stone-500">{level === 0 ? 'Home' : 'Level'}</span>
          <span className="font-bold">{level === 0 ? '🏠' : level}</span>
        </div>
        <button 
          onClick={() => setIsMuted(!isMuted)}
          className="p-2 hover:bg-stone-100 rounded-full transition-colors"
        >
          {isMuted ? <VolumeX className="w-5 h-5 text-stone-400" /> : <Volume2 className="w-5 h-5 text-stone-600" />}
        </button>
      </div>

      {/* Game Container */}
      <div className="relative rounded-3xl overflow-hidden shadow-2xl border-8 border-white bg-white">
        <canvas
          ref={canvasRef}
          width={CANVAS_WIDTH}
          height={CANVAS_HEIGHT}
          className="block bg-sky-100"
        />

        {/* Overlays */}
        <AnimatePresence>
          {gameState === 'menu' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm flex flex-col items-center justify-center text-white p-8 text-center"
            >
              <motion.h1 
                initial={{ y: -20 }}
                animate={{ y: 0 }}
                className="text-6xl font-black mb-4 tracking-tighter italic"
              >
                PIXEL QUEST
              </motion.h1>
              <p className="text-stone-300 mb-8 max-w-md">
                A classic platformer adventure. Use Arrow keys or WASD to move and Space to jump. Reach the green goal!
              </p>
              <button
                onClick={startGame}
                className="group relative flex items-center gap-3 bg-blue-500 hover:bg-blue-600 text-white px-8 py-4 rounded-2xl font-bold text-xl transition-all hover:scale-105 active:scale-95"
              >
                <Play className="w-6 h-6 fill-current" />
                START ADVENTURE
              </button>
            </motion.div>
          )}

          {gameState === 'gameOver' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="absolute inset-0 bg-red-900/80 backdrop-blur-md flex flex-col items-center justify-center text-white p-8 text-center"
            >
              <h2 className="text-5xl font-black mb-2 tracking-tighter">GAME OVER</h2>
              <p className="text-red-200 mb-8">You fell or lost all health. Try again?</p>
              <div className="flex flex-wrap gap-4 justify-center">
                <button
                  onClick={continueLevel}
                  className="flex items-center gap-3 bg-white text-blue-900 px-8 py-4 rounded-2xl font-bold text-xl hover:bg-blue-50 transition-all"
                >
                  <Play className="w-6 h-6" />
                  CONTINUE
                </button>
                <button
                  onClick={startGame}
                  className="flex items-center gap-3 bg-stone-100 text-stone-900 px-8 py-4 rounded-2xl font-bold text-xl hover:bg-stone-200 transition-all"
                >
                  <RotateCcw className="w-6 h-6" />
                  RETRY
                </button>
              </div>
            </motion.div>
          )}

          {gameState === 'win' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="absolute inset-0 bg-emerald-900/80 backdrop-blur-md flex flex-col items-center justify-center text-white p-8 text-center"
            >
              <Trophy className="w-20 h-20 text-yellow-400 mb-4" />
              <h2 className="text-5xl font-black mb-2 tracking-tighter">VICTORY!</h2>
              <p className="text-emerald-200 mb-8">You reached the goal with {score} points!</p>
              <button
                onClick={startGame}
                className="flex items-center gap-3 bg-white text-emerald-900 px-8 py-4 rounded-2xl font-bold text-xl hover:bg-emerald-50 transition-all"
              >
                <RotateCcw className="w-6 h-6" />
                PLAY AGAIN
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer / Controls Info */}
      <div className="mt-8 grid grid-cols-3 gap-8 w-full max-w-[800px]">
        <div className="bg-white p-4 rounded-2xl border border-black/5 shadow-sm">
          <div className="flex items-center gap-2 mb-2 text-stone-400">
            <Info className="w-4 h-4" />
            <span className="text-[10px] uppercase font-bold tracking-widest">Movement</span>
          </div>
          <p className="text-sm font-medium">Arrows or WASD</p>
        </div>
        <div className="bg-white p-4 rounded-2xl border border-black/5 shadow-sm">
          <div className="flex items-center gap-2 mb-2 text-stone-400">
            <Info className="w-4 h-4" />
            <span className="text-[10px] uppercase font-bold tracking-widest">Jump</span>
          </div>
          <p className="text-sm font-medium">Space or W / Up</p>
        </div>
        <div className="bg-white p-4 rounded-2xl border border-black/5 shadow-sm">
          <div className="flex items-center gap-2 mb-2 text-stone-400">
            <Info className="w-4 h-4" />
            <span className="text-[10px] uppercase font-bold tracking-widest">Goal</span>
          </div>
          <p className="text-sm font-medium">Reach the Green Block</p>
        </div>
      </div>
    </div>
  );
}
