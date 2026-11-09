// Seeded violation: a generic lambda's forwarding reference passed on without std::forward.
#include <cstdint>
#include <utility>

namespace kv::rule_28_6_2_generic_lambda::bad {

struct Payload {
  std::int32_t value;
};

std::int32_t sink(const Payload& p) { return p.value; }

std::int32_t sink(Payload&& p) { return p.value + 1; }

std::int32_t use() {
  const auto relay = [](auto&& p) { return sink(p); };
  Payload local{1};
  return relay(local) + relay(Payload{2});
}

}  // namespace kv::rule_28_6_2_generic_lambda::bad
