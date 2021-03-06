#! /usr/bin/env python

#------------------------------------------------------------------------------
class EventManager:
    """this object is responsible for coordinating most communication
    between the Model, View, and Controller."""
    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()
        self.eventQueue= []
        self.listenersToAdd = []
        self.listenersToRemove = []

    #----------------------------------------------------------------------
    def RegisterListener( self, listener ):
        self.listenersToAdd.append(listener)

    #----------------------------------------------------------------------
    def ActuallyUpdateListeners(self):
        for listener in self.listenersToAdd:
            self.listeners[ listener ] = 1
        for listener in self.listenersToRemove:
            if listener in self.listeners:
                del self.listeners[ listener ]

    #----------------------------------------------------------------------
    def UnregisterListener( self, listener ):
        self.listenersToRemove.append(listener)
        
    #----------------------------------------------------------------------
    def Post( self, event ):
        self.eventQueue.append(event)
        if isinstance(event, TickEvent):
            # Consume the event queue every Tick.
            self.ActuallyUpdateListeners()
            self.ConsumeEventQueue()

    #----------------------------------------------------------------------
    def ConsumeEventQueue(self):
        i = 0
        while i < len( self.eventQueue ):
            event = self.eventQueue[i]
            for listener in self.listeners:
                # Note: a side effect of notifying the listener
                # could be that more events are put on the queue
                # or listeners could Register / Unregister
                listener.Notify( event )
            i += 1
            if self.listenersToAdd:
                self.ActuallyUpdateListeners()
        #all code paths that could possibly add more events to 
        # the eventQueue have been exhausted at this point, so 
        # it's safe to empty the queue
        self.eventQueue= []

import Queue
class QueueEventManager(EventManager):
    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()
        self.eventQueue = Queue.Queue()
        self.listenersToAdd = []
        self.listenersToRemove = []
        
    #----------------------------------------------------------------------
    def Post( self, event ):
        self.eventQueue.put(event)
        if isinstance(event, TickEvent):
            # Consume the event queue every Tick.
            self.ActuallyUpdateListeners()
            self.ConsumeEventQueue()

    #----------------------------------------------------------------------
    def ConsumeEventQueue(self):
        try:
            while True:
                event = self.eventQueue.get(block=False)
                for listener in self.listeners:
                    # Note: a side effect of notifying the listener
                    # could be that more events are put on the queue
                    # or listeners could Register / Unregister
                    listener.Notify( event )
                if self.listenersToAdd:
                    self.ActuallyUpdateListeners()
        except Queue.Empty:
            pass # print 'queue empty', self.eventQueue


class Event:
    """this is a superclass for any events that might be generated by an
    object and sent to the EventManager"""
    def __init__(self):
        self.name = "Generic Event"
    def __str__(self):
        return '<%10s %s>' % (self.__class__.__name__, id(self))
        
class TickEvent(Event):
    def __init__(self):
        self.name = "Tick"

class EventA(Event):
    def __init__(self):
        self.name = "Event A"

class EventB(Event):
    def __init__(self):
        self.name = "Event B"

class EventC(Event):
    def __init__(self):
        self.name = "Event C"

class Listener:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)

    def __str__(self):
        return '<%20s %s>' % (self.__class__.__name__, id(self))

    def Notify(self, event):
        print self, 'got event', event

class ListenerAndPoster(Listener):
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)

    def Notify(self, event):
        print self, 'got event', event
        if isinstance(event, EventA):
            newEvent = EventC()
            self.evManager.Post(newEvent)

def main():
    evManager = EventManager()
    l1 = Listener(evManager)
    l2 = ListenerAndPoster(evManager)

    evManager.Post(EventA())
    evManager.Post(EventB())
    evManager.Post(TickEvent())

    evManager = QueueEventManager()
    l1 = Listener(evManager)
    l2 = ListenerAndPoster(evManager)

    evManager.Post(EventA())
    evManager.Post(EventB())
    evManager.Post(TickEvent())

if __name__ == '__main__':
    main()
