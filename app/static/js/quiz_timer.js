class QuizTimer {
    constructor(duration, onTick, onComplete) {
        this.duration = duration;
        this.remaining = duration;
        this.onTick = onTick;
        this.onComplete = onComplete;
        this.isPaused = false;
        this.pausesRemaining = 2;  // Allow 2 pauses per quiz
    }

    start() {
        this.interval = setInterval(() => {
            if (!this.isPaused) {
                this.remaining--;
                this.onTick(this.remaining);
                
                if (this.remaining <= 0) {
                    this.stop();
                    this.onComplete();
                }
            }
        }, 1000);
    }

    pause() {
        if (this.pausesRemaining > 0) {
            this.isPaused = true;
            this.pausesRemaining--;
            return true;
        }
        return false;
    }

    resume() {
        this.isPaused = false;
    }

    stop() {
        clearInterval(this.interval);
    }
} 