// Compliant: the object is named, so it lives for the whole scope; a discard is a cast to void.
#ifndef KV_RULE_9_2_1_OK_HPP
#define KV_RULE_9_2_1_OK_HPP

#include <cstdint>

namespace kv::rule_9_2_1::ok {

class Guard {
 public:
  explicit Guard(std::int32_t level) : level_(level) {}
  std::int32_t level() const { return level_; }

 private:
  std::int32_t level_;
};

inline std::int32_t enter(std::int32_t level) {
  const Guard guard{level};
  return guard.level();
}

}  // namespace kv::rule_9_2_1::ok

#endif  // KV_RULE_9_2_1_OK_HPP
