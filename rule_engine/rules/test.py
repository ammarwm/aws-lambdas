from durable.lang import *

with flowchart('expense'):
    # initial stage 'input' has two conditions
    with stage('input'): 
        to('request').when_all((m.subject == 'approve') & (m.amount <= 1000))
        to('deny').when_all((m.subject == 'approve') & (m.amount > 1000))
    
    # intermediate stage 'request' has an action and three conditions
    with stage('request'):
        @run
        def request(c):
            print('requesting approve')
            
        to('approve').when_all(m.subject == 'approved')
        to('deny').when_all(m.subject == 'denied')
        # reflexive condition: if met, returns to the same stage
        to('request').when_all(m.subject == 'retry')
    
    with stage('approve'):
        @run 
        def approved(c):
            print('expense approved')

    with stage('deny'):
        @run
        def denied(c):
            print('expense denied')

    @when_start
    def start(host):
        # events for the default flowchart instance, approved after retry
        host.post('expense', { 'subject': 'approve', 'amount': 100 })
        host.post('expense', { 'subject': 'retry' })
        host.post('expense', { 'subject': 'approved' })

        # events for the flowchart instance '1', denied after first try
        host.post('expense', { 'sid': 10, 'subject': 'approve', 'amount': 100})
        host.post('expense', { 'sid': 10, 'subject': 'denied'})

        # event for the flowchart instance '2' immediately denied
        host.post('expense', { 'sid': 20, 'subject': 'approve', 'amount': 10000})
        
run_all()