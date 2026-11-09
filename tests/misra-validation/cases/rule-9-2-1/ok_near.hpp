// Near misses (near): casts that are not standalone object-type casts.
#ifndef KV_RULE_9_2_1_OK_NEAR_HPP
#define KV_RULE_9_2_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_9_2_1::ok_near {

class Guard {
 public:
  explicit Guard(std::uint32_t level) : level_(level) {}
  std::uint32_t level() const { return level_; }

 private:
  std::uint32_t level_;
};

[[nodiscard]] inline std::uint32_t compute(std::uint32_t v) { return v | 1U; }

inline Guard make(std::uint32_t level) { return static_cast<Guard>(level); }

inline std::uint32_t use(std::uint32_t v) {
  static_cast<void>(compute(v));
  return make(v).level();
}

}  // namespace kv::rule_9_2_1::ok_near

#endif  // KV_RULE_9_2_1_OK_NEAR_HPP
