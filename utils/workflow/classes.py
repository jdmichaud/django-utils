from django.db import models
from django.db import transaction

import logging
from eventlog.api import log_event

# Log event definition
STATUS_HISTORY_INCONSISTENCIES  = 'status_history_inconsistencies'

################################################################################
######################## Workflow code and  models #############################
################################################################################

# The status history class that each model needing a workflow will have to
# subclass and use the model field as a ForeignKey
class StatusHistory(models.Model):
    status = models.CharField(max_length=32)
    current = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    actor = models.CharField(max_length=32) 
    # model = ...

    def __unicode__(self):
        return self.status

    class Meta:
        abstract = True

# Each states must derive from this class
class State:
    def go_next(self, obj, who): pass
    @staticmethod
    def __str__(self): raise Exception

# The Context class used to manage the workflow
# This is an implementation of the State design pattern
class Context:
    def __init__(self, 
                 model_instantiation, 
                 status_history_class,
                 state_constructor):
        self.model_instantiation = model_instantiation
        self.status_history_class = status_history_class
        self.state_constructor = state_constructor
        
        self.state = self.state_constructor(self.get_last_status().status)
#        logging.debug("state of %s[%s] at creation: %s" % (self.model_instantiation.__class__.__name__,
#                                                           self.model_instantiation.pk,
#                                                           str(self.state)))
 
    def go_next(self, who):
        if self.model_instantiation.id is None:
            raise TransitionError(str(self.state), 
                                  "", 
                                  "Save the model before going to the next state")
        self.state.go_next(self.model_instantiation, who)
       
    def setState(self, state, who):
        logging.debug(("object %s[%i]: " + str(self.state) + " -> " + str(state)) % (self.model_instantiation.__class__.__name__,
                                                                                     self.model_instantiation.pk))
        self.state = state
 
        # Update the database
        current_status = self.get_last_status(silent=True)
        current_status.current = False
        new_status = self.status_history_class(status = str(self.state),
                                               model = self.model_instantiation,
                                               current = True,
                                               actor = who)
        with transaction.atomic():
            current_status.save()
            new_status.save()
 
    # Get the last status of the object
    # No status? The object just got created, call the state constructor without
    # parameter, it will give us the default/first status for the workflow.
    def get_last_status(self, silent=True):
        if not silent:
            logging.debug("Get the last status for object %s[%s]" % (self.model_instantiation.__class__.__name__, str(self.model_instantiation.pk)))
        last_status = self.status_history_class.objects.filter(
          model__pk=self.model_instantiation.pk,
          current=True
        )
        if len(last_status) > 1: # if the table is corrupted, we silently ignore it
            log_event(STATUS_HISTORY_INCONSISTENCIES, evt_class='E',
                      message='More than one current status set for object',
                      object_class=self.model_instantiation.__class__.__name__,
                      object_id=self.model_instantiation.id)
            logging.error("Consistency error. More than one current status set for object %i already"
                          % self.model_instantiation.pk)
        if last_status: # just take the last element
            last_status = last_status[len(last_status) - 1]
            if not silent:
                logging.debug("Last status for object %s is %s" % (str(self.model_instantiation.pk), 
                                                                          last_status))
        else: # It is a new object, create the first State
            logging.debug("no state yet for model " + str(self.model_instantiation.pk) + " -> CREATED")
            last_status = self.status_history_class(status = str(self.state_constructor()),
                                                    model = self.model_instantiation,
                                                    current = True,
                                                    actor = "SYSTEM")
            if self.model_instantiation.id is not None: # If the model is not yet saved
                                                        # we can't refer to his id in the
                                                        # status history
                logging.debug("actual save for model " + str(self.model_instantiation.id))
                last_status.save()
        return last_status

    # This method to handle the special case when a model is created but we can't
    # yet save its first state. So we wait for the model to be saved and *post-save*
    # we create the first status entry for it.
    def save(self):
        logging.debug("save called for model " + str(self.model_instantiation.id))
        self.get_last_status()

#
# Exception
#

class TransitionError(Exception):
    """Raised when an operation attempts a state transition that's not
    allowed.

    Attributes:
        prev -- state at beginning of transition
        next -- attempted new state
        msg  -- explanation of why the specific transition is not allowed
    """

    def __init__(self, prev, next, msg):
        self.prev = prev
        self.next = next
        self.msg = msg
