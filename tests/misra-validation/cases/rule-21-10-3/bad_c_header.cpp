// Seeded violation: signal and raise through <signal.h>, with a volatile sig_atomic_t flag.
#include <signal.h>

namespace kv::rule_21_10_3::bad_c_header {

volatile sig_atomic_t stop_requested = 0;

void on_term(int number) { stop_requested = number; }

int arm() {
  static_cast<void>(::signal(SIGTERM, on_term));
  return raise(SIGTERM);
}

}  // namespace kv::rule_21_10_3::bad_c_header
