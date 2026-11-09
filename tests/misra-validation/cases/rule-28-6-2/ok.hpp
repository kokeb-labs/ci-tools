// Compliant: the forwarding reference keeps its value category through std::forward.
#ifndef KV_RULE_28_6_2_OK_HPP
#define KV_RULE_28_6_2_OK_HPP

#include <cstdint>
#include <utility>

namespace kv::rule_28_6_2::ok {

struct Payload {
  std::int32_t value;
};

[[nodiscard]] inline std::int32_t consume(const Payload& payload) { return payload.value; }

[[nodiscard]] inline std::int32_t consume(Payload&& payload) { return payload.value; }

template <typename T>
[[nodiscard]] std::int32_t relay(T&& payload) {
  return consume(std::forward<T>(payload));
}

[[nodiscard]] inline bool use() {
  const Payload p{1};
  return relay(p) == relay(Payload{2});
}

}  // namespace kv::rule_28_6_2::ok

#endif  // KV_RULE_28_6_2_OK_HPP
