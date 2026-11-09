// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::dir_0_3_1_infinity::bad_edge {

// A float quotient whose divisor may be zero, converted to int.
int per_item(float total, std::uint32_t items) {
  const float each = total / static_cast<float>(items);
  return static_cast<int>(each);  // seeded
}

// The same flow inside a member function.
struct Meter {
  double sum{0.0};
  long average(std::uint32_t n) const {
    const double avg = sum / n;
    return static_cast<long>(avg);  // seeded
  }
};

}  // namespace kv::dir_0_3_1_infinity::bad_edge
