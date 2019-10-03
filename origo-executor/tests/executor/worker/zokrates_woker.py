import unittest

from executor.worker.zokrates_worker import ZokratesWorker


class EthInterfaceTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_build_arguments_with_random(self):
        # test static method build_arguments
        commitments = [4]
        hashes = [89685364998030906426902553293848047120578154677247506650664740170569575157264]
        self.assertEqual(ZokratesWorker.build_arguments(commitments, [1], hashes),
                         '0 0 0 4 1 263561599766550617289250058199814760685 '
                         '65303172752238645975888084098459749904')

    def test_build_arguments_multiple_input(self):
        # test static method build_arguments
        commitments = [4, 4, 4]
        randoms = [1, 1, 1]
        hashes = [89685364998030906426902553293848047120578154677247506650664740170569575157264,
                  89685364998030906426902553293848047120578154677247506650664740170569575157264,
                  89685364998030906426902553293848047120578154677247506650664740170569575157264]
        self.assertEqual(ZokratesWorker.build_arguments(commitments, randoms, hashes),
                         '0 0 0 4 1 263561599766550617289250058199814760685 '
                         '65303172752238645975888084098459749904 '
                         '0 0 0 4 1 263561599766550617289250058199814760685 '
                         '65303172752238645975888084098459749904 '
                         '0 0 0 4 1 263561599766550617289250058199814760685 '
                         '65303172752238645975888084098459749904')
