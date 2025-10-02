from llm_benchmark.algorithms.primes import Primes
from llm_benchmark.algorithms.sort import Sort
from llm_benchmark.control.double import DoubleForLoop
from llm_benchmark.control.single import SingleForLoop
from llm_benchmark.generator.gen_list import GenList
from llm_benchmark.sql.query import SqlQuery
from llm_benchmark.datastructures.dslist import DsList
from llm_benchmark.strings.strops import StrOps

# testing 01 

def print_section_header(title):
    """Prints a formatted section header."""
    print(title)
    print("-" * len(title))
    # Add an extra newline for better spacing after the header
    print()


def single():
    print_section_header("SingleForLoop")

    print(f"sum_range(10): {SingleForLoop.sum_range(10)}")
    print(f"max_list([1, 2, 3]): {SingleForLoop.max_list([1, 2, 3])}")
    print(f"sum_modulus(100, 3): {SingleForLoop.sum_modulus(100, 3)}")
    print()


def double():
    print_section_header("DoubleForLoop")

    print(f"sum_square(10): {DoubleForLoop.sum_square(10)}")
    print(f"sum_triangle(10): {DoubleForLoop.sum_triangle(10)}")

    # Store generated list to avoid re-generating for printing and calculation
    list_for_pairs = GenList.random_list(30, 10)
    print(f"count_pairs({list_for_pairs}): {DoubleForLoop.count_pairs(list_for_pairs)}")

    # Store generated lists to avoid re-generating and for clear output
    list1_for_duplicates = GenList.random_list(10, 2)
    list2_for_duplicates = GenList.random_list(10, 2)
    print(
        f"count_duplicates({list1_for_duplicates}, {list2_for_duplicates}): "
        f"{DoubleForLoop.count_duplicates(list1_for_duplicates, list2_for_duplicates)}"
    )

    # Store generated matrix to avoid re-generating
    matrix_for_sum = GenList.random_matrix(10, 10)
    print(f"sum_matrix({matrix_for_sum}): {DoubleForLoop.sum_matrix(matrix_for_sum)}")
    print()


def sql():
    print_section_header("SQL")

    print(f"query_album('Presence'): {SqlQuery.query_album('Presence')}")
    print(f"query_album('Roundabout'): {SqlQuery.query_album('Roundabout')}")
    print()

    print("join_albums()")
    # Assuming the intent is to show only the first result for brevity
    print(SqlQuery.join_albums()[0])
    print()

    print("top_invoices()")
    print(SqlQuery.top_invoices())
    print()

def primes():
    print_section_header("Primes")

    print(f"is_prime(1700): {Primes.is_prime_ineff(1700)}")
    print(f"sum_primes(210): {Primes.sum_primes(210)}")
    print(f"prime_factors(840): {Primes.prime_factors(840)}")
    print()

def sort():
    print_section_header("Sort")

    # Demonstrate in-place sort, showing the original list for clarity
    v_sort = [5, 3, 2, 1, 4]
    original_v_sort = list(v_sort) # Make a copy to display original input
    Sort.sort_list(v_sort)
    print(f"sort_list({original_v_sort}): {v_sort}")

    # Demonstrate in-place dutch flag partition
    v_dutch = [5, 3, 2, 1, 4]
    original_v_dutch = list(v_dutch) # Make a copy to display original input
    Sort.dutch_flag_partition(v_dutch, 3)
    print(f"dutch_flag_partition({original_v_dutch}, 3): {v_dutch}")

    # Demonstrate max_n which returns a new list
    v_max_n = [5, 3, 2, 1, 4]
    print(f"max_n({v_max_n}, 3): {Sort.max_n(v_max_n, 3)}")
    print()


def dslist():
    print_section_header("DsList")

    # Use an original list and pass copies to operations that might modify in-place
    # or if the operation returns a new list, the original_test_list remains untouched.
    original_test_list = [1, 2, 3, 4, 5]
    print("Original list:", original_test_list)

    # Assuming modify_list returns a new list or modifies a copy
    modified_list = DsList.modify_list(list(original_test_list)) 
    print("Modified list:", modified_list)

    # Subsequent operations are performed on the original_test_list or its copy for clarity
    search_result = DsList.search_list(original_test_list, 3)
    print(f"Search result for 3 in {original_test_list}: {search_result}")

    sorted_list = DsList.sort_list(list(original_test_list))
    print(f"Sorted list from {original_test_list}: {sorted_list}")

    reversed_list = DsList.reverse_list(list(original_test_list))
    print(f"Reversed list from {original_test_list}: {reversed_list}")

    rotated_list = DsList.rotate_list(list(original_test_list), 2)
    print(f"Rotated list from {original_test_list} by 2 positions: {rotated_list}")

    list_to_merge = [6, 7, 8]
    merged_list = DsList.merge_lists(list(original_test_list), list_to_merge)
    print(f"Merged list with {original_test_list} and {list_to_merge}: {merged_list}")
    print()

def strops():
    print_section_header("Strops")

    test_str = "racecar"
    print("Original string:", test_str)

    reversed_str = StrOps.str_reverse(test_str)
    print("Reversed string:", reversed_str)

    is_palindrome = StrOps.palindrome(test_str)
    print("Is palindrome:", is_palindrome)
    print() # Add a newline for consistency


def main():
    single()
    double()
    sql()
    primes()
    sort()
    dslist()
    strops()


if __name__ == "__main__":
    main()