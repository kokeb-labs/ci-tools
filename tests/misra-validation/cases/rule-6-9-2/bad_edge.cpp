// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_9_2::bad_edge {

struct Packet {
  short id;
  unsigned length;
};
long long total(const Packet& p, unsigned char flags) { return p.id + static_cast<long long>(p.length) + flags; }

}  // namespace kv::rule_6_9_2::bad_edge
