// Compliant near miss: a generic lambda that forwards its auto&& parameter with std::forward.
#ifndef KV_RULE_28_6_2_GENERIC_LAMBDA_OK_HPP
#define KV_RULE_28_6_2_GENERIC_LAMBDA_OK_HPP

#include <cstdint>
#include <utility>

namespace kv::rule_28_6_2_generic_lambda::ok {

struct Payload {
  std::int32_t value;
};

[[nodiscard]] inline std::int32_t sink(const Payload& p) { return p.value; }

[[nodiscard]] inline std::int32_t sink(Payload&& p) { return p.value; }

[[nodiscard]] inline bool same() {
  const auto relay = [](auto&& p) { return sink(std::forward<decltype(p)>(p)); };
  const Payload local{1};
  return relay(local) == relay(Payload{1});
}

}  // namespace kv::rule_28_6_2_generic_lambda::ok

#endif  // KV_RULE_28_6_2_GENERIC_LAMBDA_OK_HPP
