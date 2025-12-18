from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from config import Config
from models import db, Event, Resource, EventResourceAllocation

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

def has_conflict(resource_id, start, end):
    allocations = EventResourceAllocation.query.join(Event)\
        .filter(EventResourceAllocation.resource_id == resource_id).all()
    for alloc in allocations:
        e = alloc.event
        if start < e.end_time and end > e.start_time:
            return True
    return False

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/events')
def events():
    return render_template('events.html', events=Event.query.all())

@app.route('/event/new', methods=['GET','POST'])
def new_event():
    if request.method == 'POST':
        event = Event(
            title=request.form['title'],
            start_time=datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M'),
            end_time=datetime.strptime(request.form['end_time'], '%Y-%m-%dT%H:%M'),
            description=request.form['description']
        )
        db.session.add(event)
        db.session.commit()
        flash("Event Created", "success")
        return redirect(url_for('events'))
    return render_template('event_form.html')

@app.route('/resources')
def resources():
    return render_template('resources.html', resources=Resource.query.all())

@app.route('/resource/new', methods=['GET','POST'])
def new_resource():
    if request.method == 'POST':
        resource = Resource(
            name=request.form['name'],
            type=request.form['type']
        )
        db.session.add(resource)
        db.session.commit()
        flash("Resource Added", "success")
        return redirect(url_for('resources'))
    return render_template('resource_form.html')

@app.route('/allocate', methods=['GET','POST'])
def allocate():
    events = Event.query.all()
    resources = Resource.query.all()

    if request.method == 'POST':
        event = Event.query.get(int(request.form['event_id']))
        resource_id = int(request.form['resource_id'])

        if has_conflict(resource_id, event.start_time, event.end_time):
            flash("Resource already booked!", "danger")
        else:
            db.session.add(EventResourceAllocation(
                event_id=event.id,
                resource_id=resource_id
            ))
            db.session.commit()
            flash("Resource Allocated", "success")

    allocations = EventResourceAllocation.query.all()
    return render_template(
        'allocations.html',
        events=events,
        resources=resources,
        allocations=allocations
    )

@app.route('/report', methods=['GET','POST'])
def report():
    report_data = []
    if request.method == 'POST':
        start = datetime.strptime(request.form['start'], '%Y-%m-%d')
        end = datetime.strptime(request.form['end'], '%Y-%m-%d')

        for r in Resource.query.all():
            hours = 0
            upcoming = 0
            for a in EventResourceAllocation.query.filter_by(resource_id=r.id):
                e = a.event
                if start <= e.start_time <= end:
                    hours += (e.end_time - e.start_time).seconds / 3600
                if e.start_time > datetime.now():
                    upcoming += 1
            report_data.append({
                'resource': r.name,
                'hours': hours,
                'upcoming': upcoming
            })
    return render_template('report.html', report_data=report_data)

if __name__ == '__main__':
    app.run(debug=True)
