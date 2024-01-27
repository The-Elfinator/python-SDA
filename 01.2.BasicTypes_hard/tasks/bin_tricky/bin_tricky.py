from collections.abc import Sequence


def find_median(nums1: Sequence[int], nums2: Sequence[int]) -> float:
    """
    Find median of two sorted sequences. At least one of sequences should be not empty.
    :param nums1: sorted sequence of integers
    :param nums2: sorted sequence of integers
    :return: middle value if sum of sequences' lengths is odd
             average of two middle values if sum of sequences' lengths is even
    """
    n = len(nums1)
    m = len(nums2)
    if n > m:
        return find_median(nums2, nums1)
    a = nums1
    b = nums2
    int_min = -1000000000000000000000000000
    int_max = 1000000000000000000000000000
    start = 0
    end = n
    real_median_ind = (n + m + 1) // 2
    while start <= end:
        mid = (start + end) // 2
        left_a_size = mid
        left_b_size = real_median_ind - mid
        left_a = a[left_a_size - 1] if left_a_size > 0 else int_min
        left_b = b[left_b_size - 1] if left_b_size > 0 else int_min
        right_a = a[left_a_size] if left_a_size < n else int_max
        right_b = b[left_b_size] if left_b_size < m else int_max
        if left_a <= right_b and left_b <= right_a:
            if (m + n) % 2 == 0:
                return (max(left_a, left_b) + min(right_a, right_b)) / 2.0
            return max(left_a, left_b) / 1.0
        elif left_a > right_b:
            end = mid - 1
        else:
            start = mid + 1
    return 0.0
