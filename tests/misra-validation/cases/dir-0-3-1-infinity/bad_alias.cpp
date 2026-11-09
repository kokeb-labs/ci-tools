// Seeded violation: a possibly infinite quotient converted to a fixed-width alias, the form our code writes.
#include <cstdint>

namespace kv::dir_0_3_1_infinity::bad_alias {

std::int32_t mean(double sum, std::uint32_t count) {
  const double avg = sum / count;       // infinite when count is zero
  return static_cast<std::int32_t>(avg);  // seeded
}

}  // namespace kv::dir_0_3_1_infinity::bad_alias
