// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_1_1::bad_edge {

class Gauge {
 public:
  std::uint32_t peek() {
    auto f = [=]() { return level_; };
    return f();
  }

 private:
  std::uint32_t level_{0U};
};

}  // namespace kv::rule_8_1_1::bad_edge
