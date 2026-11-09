// Seeded violation: an operation that may be infinite flows into a conversion to integer.
#include <cstdint>

namespace kv::dir_0_3_1_infinity::bad {

// The query reports a conversion to a built-in integer type; a conversion to a fixed-width alias such
// as std::int32_t is not reported (see notes in case.yml).
int mean(double sum, std::uint32_t count) {
  const double avg = sum / count;  // infinite when count is zero
  return static_cast<int>(avg);
}

double attenuate(double sum, std::uint32_t count) {
  const double avg = sum / count;  // infinite when count is zero
  return 2.0 / avg;                // silently becomes zero
}

}  // namespace kv::dir_0_3_1_infinity::bad
