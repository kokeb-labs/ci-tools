#ifndef KV_RULE_16_6_1_OK_HPP
#define KV_RULE_16_6_1_OK_HPP

// Compliant: the symmetric operators are hidden friends, so both operands convert the same way.
#include <cstdint>

namespace kv::rule_16_6_1::ok {

class Ticks {
 public:
  explicit Ticks(std::uint32_t t) : t_(t) {}

  friend Ticks operator+(const Ticks& a, const Ticks& b) { return Ticks(a.t_ + b.t_); }
  friend bool operator==(const Ticks& a, const Ticks& b) { return a.t_ == b.t_; }

  Ticks& operator+=(const Ticks& other) & {
    t_ += other.t_;
    return *this;
  }

 private:
  std::uint32_t t_;
};

}  // namespace kv::rule_16_6_1::ok

#endif  // KV_RULE_16_6_1_OK_HPP
