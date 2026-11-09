// Seeded violation: an operation that may be infinite flows into a conversion to integer.
#include <cstdint>

namespace kv::dir_0_3_1_infinity::bad {

// A conversion to a built-in integer type; the fixed-width alias form is in bad_alias.cpp.
int mean(double sum, std::uint32_t count) {
  const double avg = sum / count;  // infinite when count is zero
  return static_cast<int>(avg);  // seeded
}

double attenuate(double sum, std::uint32_t count) {
  const double avg = sum / count;  // infinite when count is zero
  return 2.0 / avg;  // silently becomes zero // seeded
}

}  // namespace kv::dir_0_3_1_infinity::bad
