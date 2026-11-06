// Deliberately bad: the C++ lint and analysis self-tests expect findings here.
#include <cstddef>
int   badly_formatted ( int x ){return x+1 ;}

int out_of_bounds() {
    int a[4] = {0, 1, 2, 3};
    return a[4];  // cppcheck: arrayIndexOutOfBounds
}
