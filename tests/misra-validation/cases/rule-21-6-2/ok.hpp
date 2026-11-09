// Compliant: the allocation is owned by std::unique_ptr from the start.
#ifndef KV_RULE_21_6_2_OK_HPP
#define KV_RULE_21_6_2_OK_HPP

#include <cstdint>
#include <memory>

namespace kv::rule_21_6_2::ok {

[[nodiscard]] inline std::int32_t compute() {
  const std::unique_ptr<std::int32_t> value = std::make_unique<std::int32_t>(3);
  return *value;
}

}  // namespace kv::rule_21_6_2::ok

#endif  // KV_RULE_21_6_2_OK_HPP
