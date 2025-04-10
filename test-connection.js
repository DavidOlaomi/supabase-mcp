require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

if (!supabaseUrl || !supabaseKey) {
    console.error('Error: Missing Supabase credentials in .env file');
    process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function testConnection() {
    try {
        // Try to query the tasks table
        const { data, error } = await supabase
            .from('tasks')
            .select('*')
            .limit(5);
        
        if (error) {
            console.error('Connection test failed:', error.message);
            return;
        }
        
        console.log('Successfully connected to Supabase!');
        console.log('Tasks from database:', data);
        
    } catch (err) {
        console.error('Error testing connection:', err.message);
    }
}

testConnection();
