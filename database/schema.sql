-- Enable the necessary extensions
create extension if not exists "uuid-ossp";

-- Create users table
create table public.users (
    id uuid default uuid_generate_v4() primary key,
    username text unique not null,
    password text not null,
    email text not null,
    skills text[] default '{}',
    preferences text default '',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create events table
create table public.events (
    id uuid default uuid_generate_v4() primary key,
    event_name text not null,
    location text not null,
    required_skills text[] not null,
    urgency text not null,
    event_date date not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create notifications table
create table public.notifications (
    id uuid default uuid_generate_v4() primary key,
    username text references public.users(username) on delete cascade,
    message text not null,
    type text not null,
    related_id text,
    read boolean default false,
    timestamp timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create volunteer history table
create table public.volunteer_history (
    id uuid default uuid_generate_v4() primary key,
    username text references public.users(username) on delete cascade,
    event_id uuid references public.events(id) on delete set null,
    hours_contributed numeric,
    feedback text,
    date_volunteered date not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create indexes for better query performance
create index idx_users_username on public.users(username);
create index idx_events_event_name on public.events(event_name);
create index idx_notifications_username on public.notifications(username);
create index idx_volunteer_history_username on public.volunteer_history(username);

-- Create Row Level Security (RLS) policies
alter table public.users enable row level security;
alter table public.events enable row level security;
alter table public.notifications enable row level security;
alter table public.volunteer_history enable row level security;

-- Users policies
create policy "Users can view their own profile"
    on public.users for select
    using (auth.uid() = id);

create policy "Users can update their own profile"
    on public.users for update
    using (auth.uid() = id);

-- Events policies
create policy "Events are viewable by everyone"
    on public.events for select
    to authenticated
    using (true);

create policy "Only authorized users can create events"
    on public.events for insert
    to authenticated
    using (true);

-- Notifications policies
create policy "Users can view their own notifications"
    on public.notifications for select
    using (auth.uid() in (
        select id from public.users where username = notifications.username
    ));

create policy "Users can update their own notifications"
    on public.notifications for update
    using (auth.uid() in (
        select id from public.users where username = notifications.username
    ));

-- Volunteer history policies
create policy "Users can view their own volunteer history"
    on public.volunteer_history for select
    using (auth.uid() in (
        select id from public.users where username = volunteer_history.username
    ));

create policy "Users can add to their own volunteer history"
    on public.volunteer_history for insert
    with check (auth.uid() in (
        select id from public.users where username = volunteer_history.username
    ));