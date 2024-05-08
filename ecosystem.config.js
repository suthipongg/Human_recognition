module.exports = {
    apps: [
        {
            name: 'service-python-nova',
            // Start the Nova service using Uvicorn
            script: 'uvicorn app:app --workers 2 --host 0.0.0.0 --port 4450',
            instances: 1, // Run only one instance of Nova service
        },
        {
            name: 'service-python-manage-queue',
            // Start the queue management system
            script: 'python3 manage_queue_system.py',
        },
        {
            name: 'service-python-object-tracking',
            // Start the object tracking system
            script: 'python3 object_tracking_system.py',
        }
    ]
}
