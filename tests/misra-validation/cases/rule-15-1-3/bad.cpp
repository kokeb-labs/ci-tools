// Seeded violation: a single-argument constructor and a conversion operator that are not explicit.
#include <cstdint>

namespace kv::rule_15_1_3::bad {

class Millivolts {
 public:
  Millivolts(std::int32_t mv) : mv_(mv) {}
  operator std::int32_t() const { return mv_; }

 private:
  std::int32_t mv_;
};

}  // namespace kv::rule_15_1_3::bad
