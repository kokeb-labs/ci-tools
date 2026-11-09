// Seeded violation (twodim): a two-dimensional built-in array at namespace scope.
#include <cstdint>

namespace kv::rule_11_3_1::bad_twodim {

constexpr std::int32_t kTable[2][2] = {{1, 2}, {3, 4}};

std::int32_t corner() { return kTable[1][1]; }

}  // namespace kv::rule_11_3_1::bad_twodim
