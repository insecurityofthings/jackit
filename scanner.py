#!/usr/bin/env python

import logging, time

class scanner:

  def __init__(self, radio, ack_timeout=250, retries=1):
    self.radio = radio
    self.channels = range(2, 84)
    self.channel_index = 0

    # Format the ACK timeout and auto retry values
    self.ack_timeout = int(ack_timeout / 250) - 1
    self.ack_timeout = max(0, min(ack_timeout, 15))
    self.retries = max(0, min(retries, 15))

    self.ping_payload = '0F:0F:0F:0F'.replace(':', '').decode('hex')

  def scan(self):
    logging.info('starting scan')

    # Put the radio in promiscuous mode
    self.radio.enter_promiscuous_mode('')
    dwell_time = 0.1

    # Set the initial channel
    self.radio.set_channel(self.channels[self.channel_index])

    # Sweep through the self.channels and decode ESB packets in pseudo-promiscuous mode
    last_tune = time.time()
    
    while True:

      if len(self.channels) > 1 and time.time() - last_tune > dwell_time:
        self.channel_index = (self.channel_index + 1) % (len(self.channels))
        self.radio.set_channel(self.channels[self.channel_index])
        last_tune = time.time()

      value = self.radio.receive_payload()
      if len(value) >= 5:
        address, payload = value[0:5], value[5:]
        logging.info('ch: %02d addr: %s p: %s' % (self.channels[self.channel_index], repr(address), repr(payload)))
        return [address, payload]

  def sniff(self, address):
    self.radio.enter_sniffer_mode(''.join(chr(b) for b in address[::-1]))

  def follow(self):
    # First try pinging on the active channel
    if not self.radio.transmit_payload(self.ping_payload, self.ack_timeout, self.retries):

      # Ping failed on the active channel, so sweep through all available channels
      for _ in range(len(self.channels)):
        self.channel_index = (self.channel_index + 1) % (len(self.channels))
        self.radio.set_channel(self.channels[self.channel_index])
        
        if self.radio.transmit_payload(self.ping_payload, self.ack_timeout, self.retries):
          # Ping successful, exit out of the ping sweep
          logging.debug('Ping success on channel {0}'.format(common.channels[channel_index]))
          return True

      # Ping sweep failed
      logging.debug('Unable to ping {0}'.format(address_string))
      return False

    # Ping succeeded on the active channel
    else:
      logging.debug('Ping success on channel {0}'.format(common.channels[channel_index]))
      return True
