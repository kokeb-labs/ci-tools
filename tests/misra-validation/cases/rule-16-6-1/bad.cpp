// Seeded violation: symmetric operators + and == written as member functions.
#include <cstdint>

namespace kv::rule_16_6_1::bad {

class Ticks {
 public:
  explicit Ticks(std::uint32_t t) : t_(t) {}
  Ticks operator+(const Ticks& other) const { return Ticks(t_ + other.t_); }
  bool operator==(const Ticks& other) const { return t_ == other.t_; }

 private:
  std::uint32_t t_;
};

}  // namespace kv::rule_16_6_1::bad
