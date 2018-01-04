# coding=utf-8
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

from copy import deepcopy
from collections import defaultdict

from qrl.core import config
from qrl.generated import qrl_pb2


class AddressState(object):
    def __init__(self, protobuf_block=None):
        self._data = protobuf_block
        self.tokens = defaultdict(int)
        if protobuf_block is None:
            self._data = qrl_pb2.AddressState()
        else:
            for key in self._data.tokens:
                self.tokens[str(key).encode()] = deepcopy(self._data.tokens[key])

    @property
    def pbdata(self):
        """
        Returns a protobuf object that contains persistable data representing this object
        :return: A protobuf AddressState object
        :rtype: qrl_pb2.AddressState
        """
        for key in self.tokens:
            self._data.tokens[key] = self.tokens[key]
        return self._data

    @property
    def address(self):
        return self._data.address

    @property
    def nonce(self):
        return self._data.nonce

    @property
    def balance(self):
        return self._data.balance

    @balance.setter
    def balance(self, new_balance: int):
        self._data.balance = new_balance

    @property
    def ots_bitfield(self):
        return self._data.ots_bitfield

    @property
    def transaction_hashes(self):
        return self._data.transaction_hashes

    @property
    def latticePK_list(self):
        return self._data.latticePK_list

    @staticmethod
    def create(address: bytes, nonce: int, balance: int, ots_bitfield: list, tokens: dict):
        address_state = AddressState()

        address_state._data.address = address
        address_state._data.nonce = nonce
        address_state._data.balance = balance
        address_state._data.ots_bitfield.extend(ots_bitfield)

        for token_txhash in tokens:
            address_state.tokens[token_txhash] = tokens[token_txhash]

        return address_state

    def add_lattice_pk(self, lattice_txn):
        lattice_pk = qrl_pb2.LatticePK(txhash=lattice_txn.txhash,
                                       dilithium_pk=lattice_txn.dilithium_pk,
                                       kyber_pk=lattice_txn.kyber_pk)

        self._data.latticePK_list.MergeFrom([lattice_pk])

    def increase_nonce(self):
        self._data.nonce += 1

    @staticmethod
    def get_default(address):
        address_state = AddressState.create(address=address,
                                            nonce=config.dev.default_nonce,
                                            balance=0,
                                            ots_bitfield=[b'\x00'] * config.dev.ots_bitfield_size,
                                            tokens=dict())
        return address_state

    @staticmethod
    def address_is_valid(address: bytes) -> bool:
        if len(address) != 73:
            return False

        if address[0] != ord('Q'):
            return False

        hex_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

        for index in range(1, len(address)):
            if chr(address[index]) not in hex_chars:
                return False

        return True
