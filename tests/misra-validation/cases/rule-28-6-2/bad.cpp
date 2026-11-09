// Seeded violation: a forwarding reference passed on without std::forward, and moved instead.
#include <cstdint>
#include <utility>

namespace kv::rule_28_6_2::bad {

struct Payload {
  std::int32_t value;
};

std::int32_t consume(const Payload& payload) { return payload.value; }

std::int32_t consume(Payload&& payload) { return payload.value + 1; }

template <typename T>
std::int32_t relay(T&& payload) {
  return consume(payload);  // seeded
}

template <typename T>
std::int32_t relay_moved(T&& payload) {
  return consume(std::move(payload));  // seeded
}

std::int32_t use() {
  Payload p{1};
  return relay(p) + relay(Payload{2}) + relay_moved(Payload{3});
}

}  // namespace kv::rule_28_6_2::bad
