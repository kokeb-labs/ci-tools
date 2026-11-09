// Near misses (near): value-initialisation and default constructors.
#ifndef KV_RULE_11_6_1_OK_NEAR_HPP
#define KV_RULE_11_6_1_OK_NEAR_HPP

#include <array>
#include <cstdint>

namespace kv::rule_11_6_1::ok_near {

class Counter {
 public:
  Counter() = default;
  std::uint32_t value() const { return value_; }

 private:
  std::uint32_t value_ = 0U;
};

inline std::uint32_t zeros() {
  std::uint32_t v{};
  const std::array<std::uint32_t, 4> buffer{};
  const Counter c;
  v = v | buffer[0] | c.value();
  return v;
}

}  // namespace kv::rule_11_6_1::ok_near

#endif  // KV_RULE_11_6_1_OK_NEAR_HPP
