// Seeded violation: one of two constructors forgets a member.
#include <cstdint>

namespace kv::rule_15_1_4::bad_second {

class Timer {
 public:
  Timer() : period_(10U), count_(0U) {}
  explicit Timer(std::uint32_t period) : period_(period) {}  // seeded

  [[nodiscard]] std::uint32_t count() const { return count_; }

 private:
  std::uint32_t period_;
  std::uint32_t count_;
};

}  // namespace kv::rule_15_1_4::bad_second
