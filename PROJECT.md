# Fantasy Hockey Score Tracker - Project Roadmap

## Project Overview
Track how Yahoo Fantasy Hockey matchup scores (current and projected) change over the course of each week, then visualize the data with ESPN-style graphs showing momentum shifts.

**Core Value Proposition:** Yahoo shows current and projected scores, but you can't see HOW those projections changed over time. Did you mount a comeback? When did the projected winner flip? This tool captures and visualizes that story.

## Current Status
**Phase 1 MVP: ✅ COMPLETE (as of Feb 3, 2026)**

**What's Working:**
- Yahoo Developer App registered and authenticated
- Python environment configured (Python 3.13.2)
- yfpy library installed and operational
- OAuth authentication with token persistence
- Data collection script captures all 6 league matchups
- Live projection data successfully accessed via `_extracted_data` workaround
- CSV storage with week boundaries
- Basic matplotlib visualization generates graphs
- Can view any team's matchup progression

**Ready for:** Professional development practices, automation, and cloud deployment

---

## MVP (Phase 1): Local Data Collection & Visualization ✅ COMPLETE

### 1.1 Data Collection Script ✅
- [x] Create script to fetch current week's matchup data
- [x] Extract: timestamp, team names, current scores, projected scores
- [x] Save to CSV file with proper formatting
- [x] Test manual execution
- [x] **CRITICAL FIX:** Access live projections via `_extracted_data` instead of static projections
- [x] Capture week start/end dates from Yahoo API
- [x] Collect ALL matchups in league (not just user's team)

### 1.2 Data Storage ✅
- [x] Design CSV schema (columns, data types)
- [x] Implement append functionality (don't overwrite existing data)
- [x] Add week boundaries for historical filtering
- [x] Handle timestamp consistency
- [ ] Add data validation (ensure no duplicates, handle errors) - *Partial*
- [ ] Consider migration to SQLite for better querying - *Future*

### 1.3 Basic Visualization ✅
- [x] Read CSV data into pandas DataFrame
- [x] Create line graph: Current Score over Time
- [x] Create line graph: Projected Score over Time
- [x] Combine both on same graph with different colors
- [x] Add labels, legend, title
- [x] Save graph as image file
- [x] Dynamic y-axis based on score range (0 to max+10%)
- [x] Filter by team name for specific matchups
- [ ] Set x-axis to exact week boundaries - *In progress*
- [ ] Improve date label formatting - *Minor issue*

### 1.4 Testing & Refinement
- [x] Run for multiple data collections in one evening
- [x] Verify data accuracy against Yahoo website
- [x] Identify and fix bugs (live projection issue)
- [x] Document how to use
- [ ] Run for one full week manually (need more data points)
- [ ] Verify graph clarity with full week of data

**Success Criteria:** ✅ Can manually run collection script multiple times and generate graphs showing score progression

---

## Phase 2: Automation & Professional Development

**Goal:** Automate data collection, follow development best practices, prepare for portfolio

### 2.1 Development Best Practices 🎯 NEXT PRIORITY
- [ ] Move API credentials to environment variables
- [ ] Create .env.template for documentation
- [ ] Initialize git repository
- [ ] Create comprehensive .gitignore
- [ ] Create requirements.txt
- [ ] Initial commit with working MVP
- [ ] Reorganize code into proper structure (src/, data/, docs/)
- [ ] Add error handling throughout
- [ ] Implement proper logging (replace print statements)
- [ ] Create README.md for portfolio

### 2.2 Testing Infrastructure 🎯 HIGH PRIORITY
**Why:** Can't test automation or visualization improvements without waiting for real games

- [ ] **Mock Data Generator:**
  - [ ] Generate realistic fake matchup data
  - [ ] Simulate score progression over time
  - [ ] Create various scenarios (blowouts, close games, comebacks)
  - [ ] Output in same CSV format as real data
  - [ ] Allow specifying number of data points and time range
- [ ] **Data Validation:**
  - [ ] Prevent duplicate timestamps
  - [ ] Handle API errors gracefully
  - [ ] Verify data completeness
- [ ] **Unit Tests:**
  - [ ] Test CSV parsing
  - [ ] Test visualization with various data sets
  - [ ] Test date handling edge cases

### 2.3 Local Automation
- [ ] Research Python scheduling options:
  - [ ] schedule library (simple)
  - [ ] APScheduler (more features)
  - [ ] cron (system-level)
- [ ] Implement intelligent scheduling based on NHL game times
- [ ] Add error handling and retry logic
- [ ] Implement logging system
- [ ] Test for full week with mock data
- [ ] Test for full week with real data

### 2.4 Intelligent Collection Timing
**Goal:** Collect data more frequently during games, less during off-hours

**NHL Game Schedule (EST):**
- Weekday starts: 7:00 PM
- Weekend starts: 1:00 PM
- Latest starts: 10:30 PM (West Coast)
- Games end: ~2.5-3 hours after start

**Collection Strategy:**
```
Weekdays:
  12:00 PM - 7:00 PM:  Every 4 hours (off-peak)
  7:00 PM - 11:30 PM:  Every 1 hour (games happening)
  11:30 PM - 1:00 AM:  Every 2 hours (late games finishing)
  1:00 AM - 12:00 PM:  Every 6 hours or skip (overnight)

Weekends:
  12:00 PM - 1:00 PM:  Every 2 hours (pre-games)
  1:00 PM - 11:30 PM:  Every 1 hour (games happening)
  11:30 PM - 12:00 PM: Every 6 hours (overnight)
```

**Implementation Phases:**
- [ ] Phase 1: Hardcoded schedule (simple, reliable for regular season)
- [ ] Phase 2: NHL schedule API integration (dynamic, accounts for off-days)
- [ ] Phase 3: Adaptive timing based on remaining games in matchup

### 2.5 Cloud Hosting Research
- [ ] Investigate free/low-cost hosting options:
  - [ ] PythonAnywhere (Python-focused, free tier)
  - [ ] Railway (modern, simple deployment)
  - [ ] Render (free tier available)
  - [ ] AWS Free Tier (more complex but powerful)
  - [ ] Heroku (if free tier returns)
- [ ] Compare: costs, features, ease of use, learning value
- [ ] Choose platform based on criteria
- [ ] Document decision rationale

### 2.6 Cloud Deployment
- [ ] Move scripts to chosen cloud platform
- [ ] Set up scheduled tasks (cron jobs or platform equivalent)
- [ ] Configure environment variables securely
- [ ] Test automated collection from cloud
- [ ] Set up monitoring/notifications for errors
- [ ] Verify data persistence and access

**Success Criteria:** System runs automatically for multiple weeks without manual intervention, collecting data consistently

---

## Phase 3: Advanced Features & Analysis

**Goal:** Add deeper analytics and historical insights

### 3.1 Projected vs Actual Analysis
**Track projection accuracy over time**

- [ ] Capture initial projected score at week start
- [ ] Capture final actual score at week end
- [ ] Calculate projection accuracy:
  - [ ] Absolute error (projected - actual)
  - [ ] Percentage error
  - [ ] Winner prediction accuracy
- [ ] Create reports showing:
  - [ ] Week-by-week projection accuracy
  - [ ] Average projection error across season
  - [ ] Teams that consistently over/underperform projections
  - [ ] Projection accuracy by day of week
- [ ] Visualize projection drift over course of week
- [ ] **Consider:** Impact of mid-week roster changes on projections
  - Track when adds/drops happen
  - Note correlation between roster changes and projection shifts

### 3.2 Multi-Week History & Trends
- [ ] View graphs for any past week (dropdown or command-line arg)
- [ ] Compare multiple weeks side-by-side
- [ ] Season-long statistics:
  - [ ] Closest matchups
  - [ ] Biggest comebacks
  - [ ] Most volatile projections
  - [ ] Best Monday vs worst Monday starts
- [ ] Track weekly performance metrics

### 3.3 Enhanced Visualizations
- [ ] Add "momentum meter" showing rate of score change
- [ ] Highlight when projected winner changes
- [ ] Show game times on graph (vertical lines)
- [ ] Annotate major events (roster adds, injuries)
- [ ] Export graphs in multiple formats (PNG, PDF, SVG)
- [ ] Create weekly recap image for social sharing

---

## Phase 4: Web Dashboard for League Sharing

**Goal:** League mates can view their own matchup graphs via web interface

### 4.1 Web Framework Selection
- [ ] Research options:
  - [ ] Streamlit (easiest, Python-native)
  - [ ] Flask (flexible, lightweight)
  - [ ] FastAPI (modern, fast)
  - [ ] Django (full-featured, may be overkill)
- [ ] Build proof-of-concept
- [ ] Choose framework based on:
  - Ease of deployment
  - User authentication needs
  - Future feature requirements

### 4.2 Basic Web Interface
- [ ] Create home page with league overview
- [ ] Team selection/filtering
- [ ] Display current week matchup graph
- [ ] Show matchup summary stats
- [ ] Responsive design (mobile-friendly)

### 4.3 Multi-User Support
- [ ] Authentication system (simple, team-based)
- [ ] User-specific views
- [ ] Collect data for all league matchups automatically
- [ ] Store data organized by team/matchup
- [ ] Privacy considerations (only show user's data)

### 4.4 Historical Data Access
- [ ] Week selector dropdown
- [ ] View any past week's graph
- [ ] Season statistics dashboard
- [ ] Download historical data

### 4.5 Web Deployment & Sharing
- [ ] Deploy web app to hosting service
- [ ] Set up custom domain (optional)
- [ ] Share URL with league
- [ ] Gather feedback from users
- [ ] Iterate based on feedback
- [ ] Monitor usage and performance

**Success Criteria:** League members can visit a URL, select their team, and see their matchup graphs for current and past weeks

---

## Ideas & Future Enhancements

**Parking lot for cool ideas to explore later:**

### Notifications & Alerts
- [ ] Push notifications when projected winner changes
- [ ] Email/SMS alerts for close matchups
- [ ] Daily summary updates
- [ ] End-of-week recap with graph

### Social & Sharing
- [ ] Export graphs optimized for social media
- [ ] Weekly recap image generation
- [ ] League chat integration (Discord/Slack bot)
- [ ] Trash talk generator based on comeback wins

### Advanced Analytics
- [ ] Prediction model: ML to predict final scores better than Yahoo
- [ ] Compare score progression to league average
- [ ] Identify "clutch" players who perform better than projected
- [ ] Historical matchup analysis (head-to-head records)
- [ ] Playoff probability calculator

### Visualization Enhancements
- [ ] Interactive graphs (hover for details)
- [ ] Animated score progression (time-lapse)
- [ ] Game-by-game breakdown (which games caused swings)
- [ ] Player contribution tracking (who drove the comeback)
- [ ] Live updates during games (WebSocket integration)

### Roster Management Integration
- [ ] Waiver wire recommendations based on projected impact
- [ ] Start/sit optimizer
- [ ] Trade analyzer
- [ ] Streaming recommendations for specific stat categories

### Multi-League Support
- [ ] Track multiple Yahoo leagues
- [ ] Cross-league performance comparison
- [ ] Unified dashboard for all teams

---

## Technical Debt & Code Quality

**Things to refactor or improve as project grows:**

### Code Organization
- [ ] Separate concerns: data collection, storage, visualization, automation
- [ ] Create proper package structure
- [ ] Move configuration to config file or class
- [ ] Implement dependency injection for testing

### Error Handling
- [ ] Comprehensive try-catch blocks
- [ ] Graceful degradation (partial data better than no data)
- [ ] Retry logic with exponential backoff
- [ ] API error categorization (rate limit vs network vs auth)

### Data Management
- [ ] Database migration (SQLite or PostgreSQL)
- [ ] Data backup strategy
- [ ] Data retention policy (how long to keep?)
- [ ] Data export functionality

### Testing
- [ ] Unit tests for all core functions
- [ ] Integration tests for API interactions
- [ ] End-to-end tests for full workflows
- [ ] Test coverage reporting

### Documentation
- [ ] API documentation (docstrings)
- [ ] User documentation (how to run, deploy)
- [ ] Developer documentation (how to contribute)
- [ ] Architecture documentation (diagrams, flow charts)

### Performance
- [ ] Optimize API calls (batch requests if possible)
- [ ] Cache frequently accessed data
- [ ] Optimize graph generation
- [ ] Database query optimization

### Security
- [ ] Secure credential storage
- [ ] API key rotation capability
- [ ] Rate limiting protection
- [ ] Input validation and sanitization

---

## Learning Goals

**Skills to develop through this project:**

### Phase 1 (Completed) ✅
- [x] API authentication (OAuth 2.0)
- [x] REST API interaction
- [x] Data collection and storage (CSV)
- [x] Data visualization (matplotlib)
- [x] Python basics (functions, loops, data structures)
- [x] Debugging and problem-solving

### Phase 2 (In Progress) 🎯
- [ ] Environment variable management
- [ ] Git/GitHub workflow and best practices
- [ ] Task scheduling and automation
- [ ] Error handling and logging
- [ ] Code organization and refactoring
- [ ] Professional documentation (README, docstrings)
- [ ] Testing methodologies (unit tests, mock data)

### Phase 3 (Future)
- [ ] Cloud deployment
- [ ] Web development (Flask/Streamlit/FastAPI)
- [ ] Database design and usage
- [ ] User authentication
- [ ] Frontend development (HTML/CSS/JavaScript)
- [ ] API design (if building endpoints)

### Portfolio Skills
- [ ] Project presentation and documentation
- [ ] Technical writing
- [ ] Problem-solving articulation (the live projection discovery story)
- [ ] Full development lifecycle (idea → MVP → production)

---

## Testing Strategy

### The Challenge
Real fantasy data only updates during live NHL games. Testing features like automation, error handling, and visualization improvements requires waiting for games to happen, which slows development significantly.

### Mock Data Generator 🎯 HIGH PRIORITY
**Build before automation to enable rapid testing**

**Requirements:**
- Generate realistic fake matchup data for any time range
- Simulate score progression patterns:
  - Linear growth (steady scoring)
  - Step increases (goals scored during game periods)
  - Projection shifts (winner changes)
  - Comeback scenarios
  - Blowout scenarios
- Output in same CSV format as real collection
- Configurable parameters:
  - Number of data points
  - Time range (hours, days, full week)
  - Score ranges
  - Volatility (how much scores jump)

**Use Cases:**
- Test visualization with full week of data
- Test automation scheduling logic
- Test error handling with edge cases
- Demo the tool without waiting for real games
- Develop new features quickly

**Implementation:**
```python
# generate_mock_data.py
def generate_mock_matchup_week(
    week_number,
    num_data_points=50,
    start_date="2026-02-02",
    end_date="2026-03-01"
):
    # Generate realistic score progression
    # Include projection changes and momentum shifts
    # Return DataFrame or write to CSV
```

### Recorded Data Playback
- [ ] Save complete week of real data as "golden dataset"
- [ ] Use for regression testing
- [ ] Verify new features don't break existing functionality

### Unit Testing
- [ ] Test CSV parsing with various formats
- [ ] Test date handling and week boundary logic
- [ ] Test graph generation with different data volumes
- [ ] Test team name matching/filtering
- [ ] Test error scenarios (missing data, malformed CSV, API failures)

---

## Phase 2: Automation & Enhancement (Current Focus)

**Goal:** Automate data collection without manual intervention, follow professional development practices

### 2.1 Development Best Practices 🎯 IMMEDIATE
- [ ] Move API credentials to environment variables (.env)
- [ ] Create .env.template for documentation
- [ ] Initialize git repository
- [ ] Create comprehensive .gitignore
- [ ] Create requirements.txt with all dependencies
- [ ] Initial commit: "Initial commit - working MVP"
- [ ] Reorganize code structure (src/, data/, docs/, tests/)
- [ ] Add comprehensive error handling
- [ ] Implement logging system (replace print statements)
- [ ] Add docstrings to all functions
- [ ] Create portfolio-ready README.md

### 2.2 Mock Data Generator (for Testing)
- [ ] Design realistic score progression algorithms
- [ ] Implement configurable mock data generation
- [ ] Create various test scenarios:
  - [ ] Full week progression
  - [ ] Comeback scenario
  - [ ] Blowout scenario  
  - [ ] Projection flip scenario
  - [ ] Multiple weeks of data
- [ ] Validate mock data matches real data patterns
- [ ] Document usage in README

### 2.3 Local Automation
- [ ] Choose scheduling library (schedule vs APScheduler vs cron)
- [ ] Implement intelligent schedule based on game times:

**Collection Schedule (EST):**

**Weekdays (Mon-Fri):**
- 12:00 PM - 7:00 PM: Every 4 hours (2 collections)
- 7:00 PM - 11:30 PM: Every 1 hour (4-5 collections)  
- 11:30 PM - 1:00 AM: Every 2 hours (1 collection)
- 1:00 AM - 12:00 PM: Every 6 hours or skip (1-2 collections)

**Weekends (Sat-Sun):**
- 12:00 PM - 1:00 PM: Every 2 hours (1 collection)
- 1:00 PM - 11:30 PM: Every 1 hour (10-11 collections)
- 11:30 PM - 12:00 PM: Every 6 hours (2 collections)

**Total:** ~15-20 collections per day during active weeks

**Implementation Tasks:**
- [ ] Create scheduler script
- [ ] Implement time-based collection logic
- [ ] Add error handling (network failures, API errors)
- [ ] Add retry logic with backoff
- [ ] Implement logging for all collection attempts
- [ ] Handle week transitions (detect new week, start fresh)
- [ ] Skip collection when week is over
- [ ] Test with mock data at accelerated speed

### 2.4 Cloud Hosting Research & Selection
- [ ] Research hosting platforms:
  - [ ] **PythonAnywhere:** Python-focused, free tier, easy cron jobs
  - [ ] **Railway:** Modern, simple, good free tier
  - [ ] **Render:** Free tier, good docs, easy deployment
  - [ ] **AWS Lambda:** Serverless, may be overkill but educational
  - [ ] **Heroku:** If free tier available
  - [ ] **Fly.io:** Modern, generous free tier
- [ ] Evaluate each platform:
  - [ ] Cost (prefer free or <$5/month)
  - [ ] Ease of deployment
  - [ ] Scheduled task support
  - [ ] Python version support
  - [ ] Learning value for portfolio
  - [ ] Reliability and uptime
- [ ] Create comparison matrix
- [ ] Make decision and document reasoning

### 2.5 Cloud Deployment
- [ ] Prepare code for deployment:
  - [ ] Environment variable configuration
  - [ ] Requirements.txt verification
  - [ ] Path handling (absolute vs relative)
  - [ ] Timezone handling (EST for NHL)
- [ ] Deploy to chosen platform
- [ ] Configure scheduled tasks
- [ ] Set up monitoring and alerts
- [ ] Test automated collection for full week
- [ ] Verify data integrity from cloud
- [ ] Document deployment process

**Success Criteria:** System runs automatically for multiple weeks without manual intervention, collecting data consistently with intelligent timing

---

## Phase 3: Advanced Features

**Goal:** Add analysis capabilities and deeper insights

### 3.1 Projected vs Actual Analysis
- [ ] Track initial projection (Monday morning)
- [ ] Track final actual score (Sunday night)
- [ ] Calculate metrics:
  - [ ] Absolute error: |projected - actual|
  - [ ] Percentage error: (projected - actual) / actual
  - [ ] Winner prediction accuracy
  - [ ] Over/under performance
- [ ] Create weekly accuracy report
- [ ] Aggregate season-long statistics
- [ ] Identify patterns:
  - [ ] Teams consistently over-projected
  - [ ] Teams consistently under-projected
  - [ ] Days of week with worst accuracy
- [ ] Visualize accuracy trends
- [ ] **Consider:** Impact of roster changes on projection accuracy
  - Note when significant adds/drops occur
  - Analyze projection shifts after roster changes

### 3.2 Historical Analysis Tools
- [ ] Season performance dashboard
- [ ] Head-to-head records
- [ ] Comeback frequency analysis
- [ ] "Game of the week" identifier (closest matchups)
- [ ] Playoff race tracking
- [ ] Power rankings based on recent trends

### 3.3 Data Export & Reporting
- [ ] Export data to various formats (JSON, Excel, PDF)
- [ ] Generate weekly summary reports
- [ ] Create season recap at end of year
- [ ] Email reports (optional)

---

## Phase 4: Web Dashboard for League Sharing

**Goal:** League mates can view their own matchup graphs and stats

### 4.1 Web Framework Selection & POC
- [ ] Evaluate frameworks:
  - [ ] **Streamlit:** Fastest for data apps, Python-only
  - [ ] **Flask:** Flexible, lightweight, more control
  - [ ] **FastAPI:** Modern, fast, good for APIs
- [ ] Build proof-of-concept with chosen framework
- [ ] Test basic functionality locally
- [ ] Decide based on: ease of use, deployment options, future needs

### 4.2 Basic Web Interface
- [ ] Home page: League overview, all matchups
- [ ] Team selector/filter
- [ ] Current week matchup display
- [ ] Graph rendering in browser
- [ ] Matchup summary statistics
- [ ] Responsive design (mobile-friendly)
- [ ] Clean, professional UI

### 4.3 Authentication & Multi-User
- [ ] Simple authentication (team-specific URLs or basic login)
- [ ] User-specific data views
- [ ] Privacy considerations
- [ ] Session management

### 4.4 Historical Data Interface
- [ ] Week selector (dropdown or calendar)
- [ ] Historical graph viewing
- [ ] Season statistics page
- [ ] Data download functionality

### 4.5 Web Deployment
- [ ] Deploy to hosting platform
- [ ] Configure domain (optional)
- [ ] Set up SSL/HTTPS
- [ ] Performance optimization
- [ ] Share URL with league
- [ ] Gather and implement feedback

**Success Criteria:** Any league member can visit a URL, select their team, and see current/historical matchup graphs

---

## Ideas & Future Enhancements

**Parking lot for cool ideas to explore later:**

### Real-Time Features
- [ ] Live updates during games (WebSocket)
- [ ] Real-time notification system
- [ ] Live scoreboard view (all matchups updating)

### Predictive Features
- [ ] Machine learning model for score prediction
- [ ] Rest-of-week projections
- [ ] Playoff probability calculator
- [ ] Optimal lineup recommendations

### Social Features
- [ ] League chat/comments
- [ ] Smack talk board
- [ ] Matchup preview emails
- [ ] Weekly awards (biggest comeback, etc.)

### Mobile App
- [ ] React Native or Flutter app
- [ ] Push notifications
- [ ] Offline data viewing

### Integration Possibilities
- [ ] Discord bot for league server
- [ ] Slack integration for work leagues
- [ ] Twitter bot for automated updates
- [ ] Integration with other fantasy platforms

---

## Questions & Blockers

**Current blockers:** None - ready for Phase 2!

**Open questions for future:**
- Database: SQLite vs PostgreSQL vs stay with CSV?
- Web framework: Streamlit vs Flask?
- Hosting: Which platform offers best balance of cost/features/learning?
- Multi-league support: Is this valuable or scope creep?

---

## Resources & References

### Documentation
- Yahoo Fantasy API: https://developer.yahoo.com/fantasysports/guide/
- yfpy Documentation: https://yfpy.uberfastman.com/
- yfpy GitHub: https://github.com/uberfastman/yfpy

### League Information
- League Settings PDF: In project folder (`/mnt/project/`)
- League ID: 30102
- Game ID: 465 (2025-26 NHL season)
- Game Code: nhl

### Development Context
- Original development conversation: Claude.ai with Sonnet 4.5 (Feb 3, 2026)
- Handoff document: HANDOFF.md
- Project started: February 3, 2026
- Current phase: Transition to professional development with Claude Code

---

## Success Metrics

### Phase 1 (MVP) ✅
- [x] Can collect matchup data successfully
- [x] Can generate graphs showing score progression
- [x] Data persists across runs
- [x] Live projections captured accurately

### Phase 2 (Automation)
- [ ] Runs automatically for entire week without intervention
- [ ] Data collected at appropriate frequencies
- [ ] Errors handled gracefully with logging
- [ ] Professional git commit history
- [ ] Portfolio-ready code and documentation

### Phase 3 (Analysis)
- [ ] Projection accuracy tracked and reported
- [ ] Historical data accessible and analyzable
- [ ] Insights generated that Yahoo doesn't provide

### Phase 4 (Sharing)
- [ ] League members actively using the dashboard
- [ ] Positive feedback from users
- [ ] Reliable uptime and performance
- [ ] Feature requests being considered

---

## Notes & Lessons Learned

### Key Discoveries
1. **Live vs Static Projections:** The `team_live_projected_points` discovery was critical - without accessing `_extracted_data`, the entire project wouldn't work as intended.

2. **Week Boundaries Matter:** Yahoo's week definitions account for late games. Using their official start/end dates ensures accuracy.

3. **OAuth Token Persistence:** Setting `save_token_data_to_env_file=True` prevents re-authentication on every run.

4. **API Structure Exploration:** Sometimes the best data isn't in the documented API - need to explore internal data structures.

### Development Insights
- Start simple (CSV) before complex (database)
- Manual MVP before automation
- Test with real data before building mock systems
- Iterate based on actual usage patterns

### Collaboration Approach
- Copy/paste method helped with learning the foundations
- Ready for Claude Code to accelerate development
- Balance: efficiency in building vs understanding what's built
- Review code changes, ask questions, but don't slow progress

---

*Project initiated: February 3, 2026*
*Current phase: Professional development with Claude Code*
*Next milestone: Automation and cloud deployment*
