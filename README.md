############################################################
#This version of project 3 can successfully test cached
#Playlists,and documents the speed at which playlists are
#downloaded when already in the cache vs. when not.
#Dev1 functionality missing, but partial implementation and
#connections in separate directory labeled: 'Project3-Scylla'
############################################################

# 449 Project 3: Music Microservices
## ScyllaDB, Memcached
### Group/Roles:
1. Dev1. Jayro Alvarez
2. Dev2. Brendan Albert
3. Ops   Ian Alvarez

Check **PerformanceTimings.pdf** to see performance tests that was done to verify the use of cache

# To Start Using Our Microservices:
1. Open a terminal in Project Directory
	- It is recommended to start without any databases.  
		- Ensure this by running `rm *.db` (be sure you are in the 449-Project-3 directory!)

2. Open a terminal in Project Directory
	- Run command: `make init`. This will:
		- Run `ulimit -n 4096 && sudo kong start` and start kong
		- Run `./kong_configuring.sh`, a script to configure all microservices and
			set them up with kong's services, routes, upstreams, and targets.
		- Run `flask init` and set up the database schema
		- Run `foreman start` to spin up our 3 instances of each of the four microservices
	- Note: If you have run kong before, you must stop it before running make init.   
		- Run `sudo stop kong` and then enter your root user's password.

3. Open another terminal in Project Directory
	- Run command `make startminio`. This will:
		- Run MinIO server to give access to physical mp3 files.

4. Open another terminal in Project Directory
	- Run command `make seedapi`. This will:
		- Fill database with various data

5. The servers are now running! Go to http://localhost:8000 to see full user manual


==================================================================================
## Phase 2
==================================================================================
# 449 Project 2: Music Microservices
## Database Sharding, XSPF Playlists and Load Balancing Proxy with Kong
### Group/Roles:
1. Dev1: Brendan Albert
2. Dev2: Ian Alvarez
3. Ops:  Jayro Alvarez

==================================================================================
## Phase 1
==================================================================================
### 449 Project 1: Music Microservices
#### Group/Roles:
1. Dev1: Ian Alvarez
2. Dev2: JayroAlvarez
3. Ops:  Brendan Albert
