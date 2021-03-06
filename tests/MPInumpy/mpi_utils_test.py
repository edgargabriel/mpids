import unittest
from mpi4py import MPI
import numpy as np

from mpids.MPInumpy.mpi_utils import *
from mpids.MPInumpy.mpi_utils import _displacments_from_counts
from mpids.MPInumpy.errors import TypeError


class HelperGetters(unittest.TestCase):

    def test_get_comm_provides_default_mpi_comm(self):
        self.assertEqual(MPI.COMM_WORLD, get_comm())


    def test_get_rank_provides_mpi_process_rank(self):
        self.assertEqual(MPI.COMM_WORLD.rank, get_rank())


    def test_get_comm_size_provides_mpi_comm_size(self):
        self.assertEqual(MPI.COMM_WORLD.size, get_comm_size())


class AllGatherVTest(unittest.TestCase):

    def setUp(self):
        self.num_procs = MPI.COMM_WORLD.Get_size()
        self.rank = MPI.COMM_WORLD.Get_rank()
        self.local_scalar = np.array(self.rank)
        self.local_data_1d = np.array([self.rank] * self.num_procs)
        self.local_data_2d = \
            np.array([self.rank] * self.num_procs**2).reshape(self.num_procs,
                                                              self.num_procs)
        self.global_scalar = np.arange(self.num_procs)
        self.global_data_1d = \
            np.array([[proc] * self.num_procs for proc in range(self.num_procs)]
                ).reshape(self.num_procs, self.num_procs)
        self.global_data_2d = \
            np.array([[proc] * self.num_procs**2 for proc in range(self.num_procs)]
                ).reshape(self.num_procs**2, self.num_procs)
        self.empty = np.array([], dtype=self.local_scalar.dtype)


    def test_supplying_a_non_numpy_array_raise_type_error(self):
        data_int = 1
        data_list = [1,2]
        data_tuple = (1,2)
        data_dict = {0: 1, 2: 3}

        with self.assertRaises(TypeError):
            all_gather_v(data_int)
        with self.assertRaises(TypeError):
            all_gather_v(data_list)
        with self.assertRaises(TypeError):
            all_gather_v(data_tuple)
        with self.assertRaises(TypeError):
            all_gather_v(data_dict)


    def arrays_are_equivelant(self, array_1, array_2):
        self.assertEqual(array_1.dtype, array_2.dtype)
        self.assertEqual(array_1.shape, array_2.shape)
        self.assertEqual(array_1.size, array_2.size)
        self.assertTrue(np.alltrue((array_1) == (array_2)))


    def test_gather_empty_value_found_on_all_procs(self):
        local_data = np.array([])
        expected_gathered_data = np.array([] * self.num_procs)

        gathered_data = all_gather_v(local_data)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_single_value_found_on_all_procs(self):
        local_data = self.local_scalar
        expected_gathered_data = self.global_scalar

        gathered_data = all_gather_v(local_data)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_single_value_found_only_on_first_proc_empty_on_rest(self):
        if self.rank == 0:
            local_data = self.local_scalar
        else:
            local_data = self.empty
        expected_gathered_data = self.global_scalar[0]

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_single_value_found_only_on_last_proc_empty_on_rest(self):
        last_proc = self.num_procs - 1
        if self.rank == last_proc:
            local_data = self.local_scalar
        else:
            local_data = self.empty
        expected_gathered_data = self.global_scalar[last_proc]

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_single_value_found_only_on_middle_proc_empty_on_rest(self):
        middle_proc = self.num_procs // 2
        if self.rank == middle_proc:
            local_data = self.local_scalar
        else:
            local_data = self.empty
        expected_gathered_data = self.global_scalar[middle_proc]

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_single_value_found_only_on_first_last_proc_empty_on_rest(self):
        last_proc = self.num_procs - 1
        if self.rank == 0 or self.rank == last_proc:
            local_data = self.local_scalar
        else:
            local_data = self.empty

        expected_gathered_data = np.array([0, last_proc])

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_1d_array_found_on_all_procs(self):
        local_data = self.local_data_1d
        expected_gathered_data = self.global_data_1d

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_1d_array_found_only_on_first_proc_empty_on_rest(self):
        if self.rank == 0:
            local_data = self.local_data_1d
        else:
            local_data = self.empty
        expected_gathered_data = self.global_data_1d[0]

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_1d_array_found_only_on_last_proc_empty_on_rest(self):
        last_proc = self.num_procs - 1
        if self.rank == last_proc:
            local_data = self.local_data_1d
        else:
            local_data = self.empty
        expected_gathered_data = self.global_data_1d[last_proc]

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_1d_array_found_only_on_middle_proc_empty_on_rest(self):
        middle_proc = self.num_procs // 2
        if self.rank == middle_proc:
            local_data = self.local_data_1d
        else:
            local_data = self.empty
        expected_gathered_data = self.global_data_1d[middle_proc]

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_1d_array_found_only_on_first_last_proc_empty_on_rest(self):
        last_proc = self.num_procs - 1
        if self.rank == 0  or self.rank == last_proc:
            local_data = self.local_data_1d
        else:
            local_data = self.empty
        expected_gathered_data = np.concatenate((self.global_data_1d[0],
                             self.global_data_1d[last_proc]))

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_2d_array_found_on_all_procs(self):
        local_data = self.local_data_2d
        expected_gathered_data = self.global_data_2d

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_2d_array_found_on_first_proc_empty_on_rest(self):
        if self.rank == 0:
            local_data = self.local_data_2d
        else:
            local_data = self.empty
        expected_gathered_data = self.global_data_2d[self.global_data_2d == 0]

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_2d_array_found_on_last_proc_empty_on_rest(self):
        last_proc = self.num_procs - 1
        if self.rank == last_proc:
            local_data = self.local_data_2d
        else:
            local_data = self.empty
        expected_gathered_data = self.global_data_2d[self.global_data_2d == last_proc]

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_2d_array_found_on_middle_proc_empty_on_rest(self):
        middle_proc = self.num_procs // 2
        if self.rank == middle_proc:
            local_data = self.local_data_2d
        else:
            local_data = self.empty
        expected_gathered_data = self.global_data_2d[self.global_data_2d == middle_proc]

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_2d_array_found_on_first_last_proc_empty_on_rest(self):
        last_proc = self.num_procs - 1
        if self.rank == 0 or self.rank == last_proc:
            local_data = self.local_data_2d
        else:
            local_data = self.empty
        expected_gathered_data = \
            np.concatenate((self.global_data_2d[self.global_data_2d == 0],
                    self.global_data_2d[self.global_data_2d == last_proc]))

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_1d_array_found_on_first_proc_2d_array_found_on_rest(self):
        if self.rank == 0:
            local_data = self.local_data_1d
        else:
            local_data = self.local_data_2d
        global_data_2d_no_first = \
            self.global_data_2d[self.global_data_2d != 0].reshape(-1,
                                                                  self.num_procs)
        global_data_1d_w_first = self.global_data_1d[0].reshape(-1,
                                                                self.num_procs)
        expected_gathered_data = np.concatenate((global_data_1d_w_first,
                                                 global_data_2d_no_first))

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_1d_array_found_on_last_proc_2d_array_found_on_rest(self):
        last_proc = self.num_procs - 1
        if self.rank == last_proc:
            local_data = self.local_data_1d
        else:
            local_data = self.local_data_2d
        global_data_2d_no_last = \
            self.global_data_2d[self.global_data_2d != last_proc].reshape(-1,
                                                                          self.num_procs)
        global_data_1d_w_last = self.global_data_1d[last_proc].reshape(-1,
                                                                       self.num_procs)
        expected_gathered_data = np.concatenate((global_data_2d_no_last,
                                                 global_data_1d_w_last))

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)


    def test_gather_1d_array_found_on_middle_proc_2d_array_found_on_rest(self):
        middle_proc = self.num_procs // 2
        if self.rank == middle_proc:
            local_data = self.local_data_1d
        else:
            local_data = self.local_data_2d
        global_data_2d_up_to_mid = \
            self.global_data_2d[self.global_data_2d < middle_proc].reshape(-1,
                                                                           self.num_procs)
        global_data_2d_past_mid = \
            self.global_data_2d[self.global_data_2d > middle_proc].reshape(-1,
                                                                           self.num_procs)
        global_data_1d_w_mid = self.global_data_1d[middle_proc].reshape(-1,
                                                                        self.num_procs)
        expected_gathered_data = np.concatenate((global_data_2d_up_to_mid,
                                                 global_data_1d_w_mid,
                                                 global_data_2d_past_mid))

        gathered_data = all_gather_v(local_data, shape=expected_gathered_data.shape)
        self.arrays_are_equivelant(gathered_data, expected_gathered_data)

class AllToAllTest(unittest.TestCase):

    def setUp(self):
        self.num_procs = MPI.COMM_WORLD.Get_size()
        self.rank = MPI.COMM_WORLD.Get_rank()

    def test_supplying_a_non_numpy_array_raise_type_error(self):
        data_int = 1
        data_list = [1,2]
        data_tuple = (1,2)
        data_dict = {0: 1, 2: 3}

        with self.assertRaises(TypeError):
            all_to_all(data_int)
        with self.assertRaises(TypeError):
            all_to_all(data_list)
        with self.assertRaises(TypeError):
            all_to_all(data_tuple)
        with self.assertRaises(TypeError):
            all_to_all(data_dict)


    def test_supplying_np_array_w_len_not_equal_to_comm_size_raise_value_error(self):
        self.assertEqual(4, self.num_procs)

        with self.assertRaises(ValueError):
            all_to_all(np.arange(3))
        with self.assertRaises(ValueError):
            all_to_all(np.arange(5))


    def test_supplying_np_array_w_dims_not_equal_to_one_raise_value_error(self):

        with self.assertRaises(ValueError):
            all_to_all(np.ones((self.num_procs,1)))
        with self.assertRaises(ValueError):
            all_to_all(np.ones((self.num_procs,1,1)))


    def arrays_are_equivelant(self, array_1, array_2):
        self.assertEqual(array_1.dtype, array_2.dtype)
        self.assertEqual(array_1.shape, array_2.shape)
        self.assertEqual(array_1.size, array_2.size)
        self.assertTrue(np.alltrue((array_1) == (array_2)))


    def test_all_to_all_with_value_equal_to_rank(self):
        local_array = np.empty(self.num_procs, dtype=np.int32)
        local_array.fill(self.rank)
        expected_result = np.arange(self.num_procs, dtype=np.int32)

        result = all_to_all(local_array)
        self.arrays_are_equivelant(result, expected_result)


class AllToAllVTest(unittest.TestCase):

    def setUp(self):
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()
        self.empty_int = np.empty(0, dtype=np.int32)
        self.data_1d_int = np.array([1, 1] * self.size, dtype=np.int32)
        self.distributed_data_1d_int = np.array([1, 1], dtype=np.int32)
        self.empty_float = np.empty(0, dtype=np.float)
        self.data_1d_float = np.array([1, 1] * self.size, dtype=np.float)
        self.distributed_data_1d_float = np.array([1, 1], dtype=np.float)
        self.displacements_1d = \
            np.array([rank * 2 for rank in range(self.size)], dtype=np.int32)


    def arrays_are_equivelant(self, array_1, array_2):
        self.assertEqual(array_1.dtype, array_2.dtype)
        self.assertEqual(array_1.shape, array_2.shape)
        self.assertEqual(array_1.size, array_2.size)
        self.assertTrue(np.alltrue((array_1) == (array_2)))


    def test_displacements_from_counts_helper_method_works(self):
        """This helper method computes the displacements off of the assumption
           that the entire local array contents are being replaced.
           A correct result is one that zeros the last counts entry, adds up
           all values, and rolls all values back by one index.
        """
        #Fully populated counts
        counts = np.array([2, 2, 2, 2])
        expected_displacements = np.array([0, 2, 4, 6])
        computed_displacements = _displacments_from_counts(counts)
        self.arrays_are_equivelant(expected_displacements, computed_displacements)

        #First element populated
        counts = np.array([1, 0, 0, 0])
        expected_displacements = np.array([0, 0, 0, 0])
        computed_displacements = _displacments_from_counts(counts)
        self.arrays_are_equivelant(expected_displacements, computed_displacements)

        #Second element populated
        counts = np.array([0, 1, 0, 0])
        expected_displacements = np.array([0, 0, 0, 0])
        computed_displacements = _displacments_from_counts(counts)
        self.arrays_are_equivelant(expected_displacements, computed_displacements)

        #Third element populated
        counts = np.array([0, 0, 1, 0])
        expected_displacements = np.array([0, 0, 0, 0])
        computed_displacements = _displacments_from_counts(counts)
        self.arrays_are_equivelant(expected_displacements, computed_displacements)

        #Fourth element populated
        counts = np.array([0, 0, 0, 1])
        expected_displacements = np.array([0, 0, 0, 0])
        computed_displacements = _displacments_from_counts(counts)
        self.arrays_are_equivelant(expected_displacements, computed_displacements)

        #First two elements populated
        counts = np.array([1, 2, 0, 0])
        expected_displacements = np.array([0, 1, 1, 1])
        computed_displacements = _displacments_from_counts(counts)
        self.arrays_are_equivelant(expected_displacements, computed_displacements)

        #First and third elements populated
        counts = np.array([1, 0, 2, 0])
        expected_displacements = np.array([0, 1, 1, 1])
        computed_displacements = _displacments_from_counts(counts)
        self.arrays_are_equivelant(expected_displacements, computed_displacements)

        #First and Fourth elements populated
        counts = np.array([1, 0, 0, 3])
        expected_displacements = np.array([0, 1, 1, 1])
        computed_displacements = _displacments_from_counts(counts)
        self.arrays_are_equivelant(expected_displacements, computed_displacements)

        #Second and Third elements populated
        counts = np.array([0, 2, 1, 0])
        expected_displacements = np.array([0, 0, 2, 2])
        computed_displacements = _displacments_from_counts(counts)
        self.arrays_are_equivelant(expected_displacements, computed_displacements)

        #Second and Fourth elements populated
        counts = np.array([0, 3, 0, 9])
        expected_displacements = np.array([0, 0, 3, 3])
        computed_displacements = _displacments_from_counts(counts)
        self.arrays_are_equivelant(expected_displacements, computed_displacements)

        #Third and Fourth elements populated
        counts = np.array([0, 0, 21, 9])
        expected_displacements = np.array([0, 0, 0, 21])
        computed_displacements = _displacments_from_counts(counts)
        self.arrays_are_equivelant(expected_displacements, computed_displacements)


    def test_all_to_all_v_transfer_all_1d_int_to_all_ranks(self):
        for root in range(self.size):
            if self.rank == root:
                send_list = root * [0] + [2] + [0] * (self.size - root- 1)
                recv_list = [2] * self.size
                send_counts = np.array(send_list)
                recv_counts = np.array(recv_list)
                expected_received_array = self.data_1d_int
            else:
                send_list = root * [0] + [2] + [0] * (self.size - root - 1)
                recv_list = [0] * self.size
                send_counts = np.array(send_list)
                recv_counts = np.array(recv_list)
                expected_received_array = self.empty_int

            received_array = \
                all_to_all_v(self.distributed_data_1d_int, send_counts, recv_counts)

            self.arrays_are_equivelant(received_array, expected_received_array)


    def test_all_to_all_v_transfer_all_1d_float_to_all_ranks(self):
        for root in range(self.size):
            if self.rank == root:
                send_list = root * [0] + [2] + [0] * (self.size - root- 1)
                recv_list = [2] * self.size
                send_counts = np.array(send_list)
                recv_counts = np.array(recv_list)
                expected_received_array = self.data_1d_float
            else:
                send_list = root * [0] + [2] + [0] * (self.size - root - 1)
                recv_list = [0] * self.size
                send_counts = np.array(send_list)
                recv_counts = np.array(recv_list)
                expected_received_array = self.empty_float

            received_array = \
                all_to_all_v(self.distributed_data_1d_float, send_counts, recv_counts)

            self.arrays_are_equivelant(received_array, expected_received_array)


    def test_all_to_all_v_transfer_all_1d_int_to_all_ranks_w_displacements(self):
        for root in range(self.size):
            if self.rank == root:
                send_list = root * [0] + [2] + [0] * (self.size - root- 1)
                recv_list = [2] * self.size
                send_counts = np.array(send_list)
                recv_counts = np.array(recv_list)
                send_displacements = np.array([0] * self.size)
                recv_displacements = np.array([0, 2, 4, 6])
                expected_received_array = self.data_1d_int
            else:
                send_list = root * [0] + [2] + [0] * (self.size - root - 1)
                recv_list = [0] * self.size
                send_counts = np.array(send_list)
                recv_counts = np.array(recv_list)
                send_displacements = np.array([0] * self.size)
                recv_displacements = np.array([0] * self.size)
                expected_received_array = self.empty_int

            received_array = \
                all_to_all_v(self.distributed_data_1d_int, send_counts, recv_counts,
                             send_displacements, recv_displacements)

            self.arrays_are_equivelant(received_array, expected_received_array)


    def test_all_to_all_v_transfer_all_1d_int_to_all_ranks_changing_shape(self):
        for root in range(self.size):
            if self.rank == root:
                send_list = root * [0] + [2] + [0] * (self.size - root- 1)
                recv_list = [2] * self.size
                send_counts = np.array(send_list)
                recv_counts = np.array(recv_list)
                recv_shape = (1, self.data_1d_int.size)
                expected_received_array = self.data_1d_int.reshape(1, self.data_1d_int.size)
            else:
                send_list = root * [0] + [2] + [0] * (self.size - root - 1)
                recv_list = [0] * self.size
                send_counts = np.array(send_list)
                recv_counts = np.array(recv_list)
                send_displacements = np.array([0] * self.size)
                recv_displacements = np.array([0] * self.size)
                recv_shape = (0, 0)
                expected_received_array = self.empty_int.reshape(0, 0)

            received_array = \
                all_to_all_v(self.distributed_data_1d_int, send_counts, recv_counts,
                             recv_shape=recv_shape)

            self.arrays_are_equivelant(received_array, expected_received_array)


class BroadcastShapeTest(unittest.TestCase):

    def setUp(self):
        self.shape_1d = np.arange(25).shape
        self.shape_2d = np.arange(25).reshape(5,5).shape
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()


    def test_broadcasting_1d_shape_from_all_ranks(self):
        for root in range(self.size):
            local_shape = None
            self.assertTrue(local_shape is None)
            if self.rank == root:
                local_shape = self.shape_1d
            local_shape = broadcast_shape(local_shape, comm=self.comm, root=root)
            self.assertEqual(local_shape, self.shape_1d)


    def test_broadcasting_2d_shape_from_all_ranks(self):
        for root in range(self.size):
            local_shape = None
            self.assertTrue(local_shape is None)
            if self.rank == root:
                local_shape = self.shape_2d
            local_shape = broadcast_shape(local_shape, comm=self.comm, root=root)
            self.assertEqual(tuple(local_shape), self.shape_2d)


class BroadcastArrayTest(unittest.TestCase):

    def setUp(self):
        self.data_1d_int = np.arange(25, dtype = np.int32)
        self.data_1d_float = np.arange(25, dtype = np.float)
        self.data_2d_int = np.arange(25, dtype = np.int32).reshape(5,5)
        self.data_2d_float = np.arange(25, dtype = np.float).reshape(5,5)
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()


    def arrays_are_equivelant(self, array_1, array_2):
        self.assertEqual(array_1.dtype, array_2.dtype)
        self.assertEqual(array_1.shape, array_2.shape)
        self.assertEqual(array_1.size, array_2.size)
        self.assertTrue(np.alltrue((array_1) == (array_2)))


    def test_broadcasting_1d_int_array_from_all_ranks(self):
        for root in range(self.size):
            local_data = None
            self.assertTrue(local_data is None)
            if self.rank == root:
                local_data = self.data_1d_int
            local_data = broadcast_array(local_data, comm=self.comm, root=root)
            self.arrays_are_equivelant(local_data, self.data_1d_int)


    def test_broadcasting_1d_float_array_from_all_ranks(self):
        for root in range(self.size):
            local_data = None
            self.assertTrue(local_data is None)
            if self.rank == root:
                local_data = self.data_1d_float
            local_data = broadcast_array(local_data, comm=self.comm, root=root)
            self.arrays_are_equivelant(local_data, self.data_1d_float)


    def test_broadcasting_2d_int_array_from_all_ranks(self):
        for root in range(self.size):
            local_data = None
            self.assertTrue(local_data is None)
            if self.rank == root:
                local_data = self.data_2d_int
            local_data = broadcast_array(local_data, comm=self.comm, root=root)
            self.arrays_are_equivelant(local_data, self.data_2d_int)


    def test_broadcasting_2d_float_array_from_all_ranks(self):
        for root in range(self.size):
            local_data = None
            self.assertTrue(local_data is None)
            if self.rank == root:
                local_data = self.data_2d_float
            local_data = broadcast_array(local_data, comm=self.comm, root=root)
            self.arrays_are_equivelant(local_data, self.data_2d_float)


class ScatterVTest(unittest.TestCase):

    def setUp(self):
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()
        self.data_1d_int = np.array([1, 1] * self.size, dtype=np.int32)
        self.expected_data_1d_int = np.array([1, 1], dtype=np.int32)
        self.data_1d_float = np.array([1, 1] * self.size, dtype=np.float)
        self.expected_data_1d_float = np.array([1, 1], dtype=np.float)
        self.displacements_1d = \
            np.array([rank * 2 for rank in range(self.size)], dtype=np.int32)
        self.shapes_1d = np.array([2] * self.size, dtype=np.int32)
        self.data_2d_int = \
            np.array([1, 1, 1, 1] * self.size, dtype=np.int32).reshape(self.size * 2, 2)
        self.expected_data_2d_int = np.array([1, 1, 1, 1], dtype=np.int32).reshape(2,2)
        self.data_2d_float = \
            np.array([1, 1, 1, 1] * self.size, dtype=np.float).reshape(self.size * 2, 2)
        self.expected_data_2d_float = np.array([1, 1, 1, 1], dtype=np.float).reshape(2,2)
        self.displacements_2d = \
            np.array([rank * 4 for rank in range(self.size)], dtype=np.int32)
        self.shapes_2d = \
            np.array([2, 2] * self.size, dtype=np.int32).reshape(self.size, 2)


    def arrays_are_equivelant(self, array_1, array_2):
        self.assertEqual(array_1.dtype, array_2.dtype)
        self.assertEqual(array_1.shape, array_2.shape)
        self.assertEqual(array_1.size, array_2.size)
        self.assertTrue(np.alltrue((array_1) == (array_2)))


    def test_scatter_v_1d_int_array_from_all_ranks(self):
        for root in range(self.size):
            local_data = None
            shapes = None
            displacements = None
            self.assertTrue(local_data is None)
            self.assertTrue(shapes is None)
            self.assertTrue(displacements is None)
            if self.rank == root:
                local_data = self.data_1d_int
                shapes = self.shapes_1d
                displacements = self.displacements_1d
            local_data = \
                scatter_v(local_data, displacements, shapes, self.comm, root=root)
            self.arrays_are_equivelant(local_data, self.expected_data_1d_int)


    def test_scatter_v_1d_float_array_from_all_ranks(self):
        for root in range(self.size):
            local_data = None
            shapes = None
            displacements = None
            self.assertTrue(local_data is None)
            self.assertTrue(shapes is None)
            self.assertTrue(displacements is None)
            if self.rank == root:
                local_data = self.data_1d_float
                shapes = self.shapes_1d
                displacements = self.displacements_1d
            local_data = \
                scatter_v(local_data, displacements, shapes, self.comm, root=root)
            self.arrays_are_equivelant(local_data, self.expected_data_1d_float)


    def test_scatter_v_2d_int_array_from_all_ranks(self):
        for root in range(self.size):
            local_data = None
            shapes = None
            displacements = None
            self.assertTrue(local_data is None)
            self.assertTrue(shapes is None)
            self.assertTrue(displacements is None)
            if self.rank == root:
                local_data = self.data_2d_int
                shapes = self.shapes_2d
                displacements = self.displacements_2d
            local_data = \
                scatter_v(local_data, displacements, shapes, self.comm, root=root)
            self.arrays_are_equivelant(local_data, self.expected_data_2d_int)


    def test_scatter_v_2d_float_array_from_all_ranks(self):
        for root in range(self.size):
            local_data = None
            shapes = None
            displacements = None
            self.assertTrue(local_data is None)
            self.assertTrue(shapes is None)
            self.assertTrue(displacements is None)
            if self.rank == root:
                local_data = self.data_2d_float
                shapes = self.shapes_2d
                displacements = self.displacements_2d
            local_data = \
                scatter_v(local_data, displacements, shapes, self.comm, root=root)
            self.arrays_are_equivelant(local_data, self.expected_data_2d_float)


if __name__ == '__main__':
    unittest.main()
