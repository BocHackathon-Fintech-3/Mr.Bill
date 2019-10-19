from django.utils.dateparse import parse_datetime

NLP_APPROVAL_THRESHOLD = 0.85


class MsgTypes(object):
    UNKNOWN = 'u'
    # NLP = 'nlp' //the message is not nlp. it HAS NLP elements though
    TEXT = 'text'
    POSTBACK = 'postback'


class MsgContentTypes(object):
    TIMESTAMP = 'timestamp'
    DURATION = 'duration'
    COMMAND = 'command'
    PHONE = 'phone'
    EMAIL = 'email'
    TEXT = 'text'
    UNKNOWN = 'u'


# class CmdParser(object):
#     def __init__(self, cmd, params={}, namespace='global'):
#         pass

class MsgUtils(object):
    @classmethod
    def encode_postback_command(cls, cmd, params={}, namespace='global'):
        # ':' and '|' are forbidden as param key/values as they are used for seperating the encoded values
        # takes a string and a set of params, and encodes them to a single string to be given as a postback command to facebook
        string_elements = []
        for key, value in params.items():
            string_elements.append("%s:%s" % (key, value))

        param_string = '|'.join(string_elements)
        if len(param_string):
            return "%s|%s~%s" % (namespace, cmd, param_string)
        else:
            return "%s|%s" % (namespace, cmd)

    @classmethod
    def decode_postback_command(cls, encoded_cmd):
        if encoded_cmd == '<get_started>':
            return ('global', 'get_started', {})

        try:
            cmd_part, params_part = encoded_cmd.split('~')
        except ValueError:
            cmd_part = encoded_cmd
            params_part = ""
        params = {}
        namespace, cmd = cmd_part.split("|")
        if len(params_part):
            for element in params_part.split('|'):
                key, val = element.split(':')
                params[key] = val
        return (namespace, cmd, params)


class MsgClassifier(object):
    def __init__(self, msg):
        self._msg = msg
        self.msg_type = MsgTypes.UNKNOWN
        self.msg_content = MsgContentTypes.UNKNOWN

        # used for POSTBACK messages
        self._cmd = None
        self._cmd_params = None

        # use for TEXT messages
        self._text = ""
        self._attachment = None
        self._nlp_entities = {}

        self._classify()

    def _classify(self):
        msg = self._msg
        if msg.get('postback'):
            self.msg_type = MsgTypes.POSTBACK
            self._parse_payload(msg['postback']['payload'])
        elif msg.get('message'):
            self.msg_type = MsgTypes.TEXT
            self._parse_text(msg['message'])
            # During the parsing, we should save the actual text, and also grab any NLP entities that were found.
            # Then the classifier can answer qwuestions like is_phone, or is_email, or is_datetime.
            # Each flow can then choose WHICH nlp entities are important to it, and check for the existance of those!
        else:
            self.msg_type = MsgTypes.UNKNOWN

    def _parse_payload(self, payload):
        namespace, cmd, params = MsgUtils.decode_postback_command(payload)
        self._cmd = cmd
        self._cmd_params = params
        self._cmd_namespace = namespace

    def _parse_text(self, message):
        if message.get('attachments'):
            if message['attachments']['sticker_id'] == 369239263222822:  # A thumbs up of facebook
                self._nlp_entities['approval'] = {
                    'confidence': 1,
                    'val': True
                }
            else:
                self._attachment = None
                pass
        if message.get('text'):
            self._text = message.get('text')

        # https://developers.facebook.com/docs/messenger-platform/built-in-nlp/
        if 'nlp' in message:
            for key, val in message['nlp']['entities'].items():
                entity = val[0]
                # if entity['confidence'] > NLP_APPROVAL_THRESHOLD:
                # Then it's a strong discover. save it!
                self._nlp_entities[key] = entity

    def is_get_started(self):
        return self._cmd == '<get_started>'

    def is_postback(self):
        return self.msg_type == MsgTypes.POSTBACK

    def get_cmd(self):
        return self._cmd

    def get_params(self):
        return self._cmd_params

    def get_namespace(self):
        return self._cmd_namespace

    def get_text(self):
        return self._text

    def is_text(self):
        return self.msg_type == MsgTypes.TEXT

    def _is_nlp_entity(self, nlp_entity):
        if nlp_entity in self._nlp_entities:
            if self._nlp_entities[nlp_entity]['confidence'] >= NLP_APPROVAL_THRESHOLD:
                return True
        return False

    def _might_be_nlp_entity(self, nlp_entity):
        if nlp_entity in self._nlp_entities:
            return True
        return False

    def is_phone(self):
        return self._is_nlp_entity('phone_number')

    def might_be_phone(self):
        return self._might_be_nlp_entity('phone_number')

    def is_email(self):
        return self._is_nlp_entity('email')

    def might_be_email(self):
        return self._might_be_nlp_entity('email')

    def is_greeting(self):
        return self._is_nlp_entity('greetings')

    def might_be_greeting(self):
        return self._might_be_nlp_entity('greetings')

    def is_thankyou(self):
        return self._is_nlp_entity('thanks')

    def might_be_thankyou(self):
        return self._might_be_nlp_entity('thanks')

    def is_timestamp(self):
        if 'datetime' in self._nlp_entities:
            if 'value' in self._nlp_entities['datetime']:
                return True
        return False

    def get_timestamp(self):
        timestamp_str = self._nlp_entities['datetime']['value']
        return parse_datetime(timestamp_str)

    def is_duration(self):
        if 'datetime' in self._nlp_entities:
            if 'type' in self._nlp_entities['datetime']:
                return True
        return False

    def get_duration_timestamps(self):
        # Should read the nlp entity and return back two timestamps.
        # This shouold be called only if is_duration() holds
        from_timestamp = self._nlp_entities['datetime']['from']['value']
        to_timestamp = self._nlp_entities['datetime']['from']['to']
        return (from_timestamp, to_timestamp)

    def get_phone(self):
        return self._nlp_entities['phone_number']['value']

    def get_email(self):
        return self._nlp_entities['email']['value']
